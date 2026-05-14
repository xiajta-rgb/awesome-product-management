from datetime import datetime

from sqlalchemy.orm import sessionmaker

from src.common.database import engine, UserPreference, PushRecord


class PushSettingsManager:
    VALID_GENDER_FOCUSES = ["male", "female", "unisex"]
    VALID_HEAT_PREFERENCES = ["high", "medium", "low", "all"]
    VALID_PUSH_CHANNELS = ["email", "sms", "app", "wechat"]
    VALID_PUSH_FREQUENCIES = ["realtime", "daily", "weekly"]

    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def set_user_preference(self, user_id, preferences):
        session = self.Session()
        try:
            existing = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            if existing:
                if "gender_focus" in preferences:
                    existing.gender_focus = preferences["gender_focus"]
                if "category_focus" in preferences:
                    existing.category_focus = preferences["category_focus"]
                if "heat_preference" in preferences:
                    existing.heat_preference = preferences["heat_preference"]
                if "uniqueness_threshold" in preferences:
                    existing.uniqueness_threshold = preferences["uniqueness_threshold"]
                if "push_channels" in preferences:
                    existing.push_channels = preferences["push_channels"]
                if "push_frequency" in preferences:
                    existing.push_frequency = preferences["push_frequency"]
                existing.updated_at = datetime.now()
                session.commit()
                pref_data = self._preference_to_dict(existing)
                return {"success": True, "action": "updated", "data": pref_data}
            else:
                new_pref = UserPreference(
                    user_id=user_id,
                    gender_focus=preferences.get("gender_focus"),
                    category_focus=preferences.get("category_focus"),
                    heat_preference=preferences.get("heat_preference"),
                    uniqueness_threshold=preferences.get("uniqueness_threshold"),
                    push_channels=preferences.get("push_channels"),
                    push_frequency=preferences.get("push_frequency"),
                )
                session.add(new_pref)
                session.commit()
                pref_data = self._preference_to_dict(new_pref)
                return {"success": True, "action": "created", "data": pref_data}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def get_user_preference(self, user_id):
        session = self.Session()
        try:
            pref = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            if pref:
                return {"success": True, "data": self._preference_to_dict(pref)}
            else:
                return {"success": False, "error": "User preference not found"}
        finally:
            session.close()

    def filter_by_category(self, products, gender_focus=None, category_focus=None):
        filtered = products
        if gender_focus:
            filtered = [
                p for p in filtered
                if p.get("gender_focus") == gender_focus
                or p.get("gender") == gender_focus
                or p.get("gender_focus") == "unisex"
            ]
        if category_focus:
            filtered = [
                p for p in filtered
                if p.get("category_main") == category_focus
                or p.get("category_sub") == category_focus
                or p.get("category") == category_focus
            ]
        return filtered

    def filter_by_heat(self, trends, heat_preference=None):
        if not heat_preference or heat_preference == "all":
            return trends
        filtered = [
            t for t in trends
            if t.get("heat_level") == heat_preference
        ]
        return filtered

    def set_uniqueness_threshold(self, user_id, threshold):
        session = self.Session()
        try:
            pref = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            if pref:
                old_value = pref.uniqueness_threshold
                pref.uniqueness_threshold = threshold
                pref.updated_at = datetime.now()
                session.commit()
                return {
                    "success": True,
                    "old_value": old_value,
                    "new_value": threshold,
                }
            else:
                new_pref = UserPreference(
                    user_id=user_id,
                    uniqueness_threshold=threshold,
                )
                session.add(new_pref)
                session.commit()
                return {"success": True, "old_value": None, "new_value": threshold}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def trigger_manual_push(self, user_id, push_type):
        session = self.Session()
        try:
            pref = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            push_channel = pref.push_channels if pref else "app"
            if "," in str(push_channel):
                push_channel = str(push_channel).split(",")[0].strip()
            record = PushRecord(
                user_id=user_id,
                push_type=push_type,
                push_content=f"Manual push triggered: {push_type}",
                push_channel=push_channel,
                push_status="sent",
            )
            session.add(record)
            session.commit()
            return {
                "success": True,
                "push_type": push_type,
                "push_channel": push_channel,
                "record_id": record.id,
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def _preference_to_dict(self, pref):
        return {
            "id": pref.id,
            "user_id": pref.user_id,
            "gender_focus": pref.gender_focus,
            "category_focus": pref.category_focus,
            "heat_preference": pref.heat_preference,
            "uniqueness_threshold": pref.uniqueness_threshold,
            "push_channels": pref.push_channels,
            "push_frequency": pref.push_frequency,
            "created_at": pref.created_at.isoformat() if pref.created_at else None,
            "updated_at": pref.updated_at.isoformat() if pref.updated_at else None,
        }
