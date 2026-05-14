import glob
import os
import shutil
from datetime import datetime

from src.algorithm.rule_file import RuleFileManager


class RuleManager:
    DEFAULT_RULE_PATH = "config/rule.json"

    def __init__(self):
        self.rule_file_manager = RuleFileManager()

    def view_rule_file(self, filepath=None):
        filepath = filepath or self.DEFAULT_RULE_PATH
        try:
            rule_data = self.rule_file_manager.load_rule_file(filepath)
            return {"success": True, "data": rule_data, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e), "filepath": filepath}

    def edit_rule_section(self, section, new_values, filepath=None):
        filepath = filepath or self.DEFAULT_RULE_PATH
        try:
            rule_data = self.rule_file_manager.update_rule_section(section, new_values, filepath)
            return {"success": True, "data": rule_data, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e), "filepath": filepath}

    def save_rule_file(self, rule_data, filepath):
        try:
            self.rule_file_manager.save_rule_file(rule_data, filepath)
            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e), "filepath": filepath}

    def backup_rule_file(self, filepath=None):
        filepath = filepath or self.DEFAULT_RULE_PATH
        try:
            backup_path = self.rule_file_manager.backup_rule_file(filepath)
            if backup_path:
                return {"success": True, "backup_filepath": backup_path, "source_filepath": filepath}
            else:
                return {"success": False, "error": "Rule file not found", "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e), "filepath": filepath}

    def list_rule_backups(self):
        rule_dir = os.path.dirname(self.DEFAULT_RULE_PATH) or "."
        rule_name = os.path.basename(self.DEFAULT_RULE_PATH)
        pattern = os.path.join(rule_dir, f"{rule_name}.backup_*")
        backup_files = sorted(glob.glob(pattern), reverse=True)
        backups = []
        for bf in backup_files:
            stat = os.stat(bf)
            backups.append({
                "filepath": bf,
                "size": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        return backups

    def restore_rule_backup(self, backup_filepath):
        try:
            if not os.path.exists(backup_filepath):
                return {"success": False, "error": "Backup file not found"}
            target_path = self.DEFAULT_RULE_PATH
            if backup_filepath.startswith(target_path + ".backup_"):
                shutil.copy2(backup_filepath, target_path)
                rule_data = self.rule_file_manager.load_rule_file(target_path)
                return {"success": True, "restored_to": target_path, "data": rule_data}
            else:
                return {"success": False, "error": "Invalid backup file path"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def adjust_weight(self, section, param, value, filepath=None):
        filepath = filepath or self.DEFAULT_RULE_PATH
        try:
            rule_data = self.rule_file_manager.load_rule_file(filepath)
            if section not in rule_data:
                return {"success": False, "error": f"Section '{section}' not found"}
            if "weights" not in rule_data[section]:
                return {"success": False, "error": f"'weights' not found in section '{section}'"}
            if param not in rule_data[section]["weights"]:
                return {"success": False, "error": f"Weight parameter '{param}' not found in section '{section}'"}
            old_value = rule_data[section]["weights"][param]
            rule_data[section]["weights"][param] = value
            rule_data["updated_at"] = datetime.now().isoformat()
            self.rule_file_manager.save_rule_file(rule_data, filepath)
            return {
                "success": True,
                "section": section,
                "param": param,
                "old_value": old_value,
                "new_value": value,
                "filepath": filepath,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def adjust_threshold(self, section, param, value, filepath=None):
        filepath = filepath or self.DEFAULT_RULE_PATH
        try:
            rule_data = self.rule_file_manager.load_rule_file(filepath)
            if section not in rule_data:
                return {"success": False, "error": f"Section '{section}' not found"}
            if param not in rule_data[section]:
                return {"success": False, "error": f"Parameter '{param}' not found in section '{section}'"}
            old_value = rule_data[section][param]
            rule_data[section][param] = value
            rule_data["updated_at"] = datetime.now().isoformat()
            self.rule_file_manager.save_rule_file(rule_data, filepath)
            return {
                "success": True,
                "section": section,
                "param": param,
                "old_value": old_value,
                "new_value": value,
                "filepath": filepath,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
