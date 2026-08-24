import json
from datetime import datetime

class SystemAuditTrail:
    def __init__(self):
        self.action_history = []

    def log(self, event_data):
        # Capture the event from the agents and add a timestamp
        event_data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.action_history.append(event_data)

    def save_audit_log(self, export_path="final_agent_audit.json"):
        with open(export_path, "w") as json_file:
            json.dump(self.action_history, json_file, indent=4)

# Create the instance that David's Critic agent is expecting to import
audit_logger = SystemAuditTrail()