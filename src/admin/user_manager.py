import json
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from src.common.database import engine, UserPreference, PushRecord, SystemLog


class UserManager:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def get_user_preferences(self, user_id):
        session = self.Session()
        try:
            pref = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            if pref:
                return {
                    "success": True,
                    "data": {
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
                    },
                }
            else:
                return {"success": False, "error": "User preference not found"}
        finally:
            session.close()

    def get_push_records(self, user_id, limit=50):
        session = self.Session()
        try:
            query = (
                session.query(PushRecord)
                .filter(PushRecord.user_id == user_id)
                .order_by(PushRecord.created_at.desc())
                .limit(limit)
            )
            results = query.all()
            records = []
            for row in results:
                records.append({
                    "id": row.id,
                    "user_id": row.user_id,
                    "push_type": row.push_type,
                    "push_content": row.push_content,
                    "push_channel": row.push_channel,
                    "push_status": row.push_status,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
            return records
        finally:
            session.close()

    def collect_feedback(self, user_id, feedback):
        session = self.Session()
        try:
            log_content = json.dumps({
                "user_id": user_id,
                "feedback": feedback,
            }, ensure_ascii=False)
            log_entry = SystemLog(
                log_type="user_feedback",
                log_content=log_content,
                status="received",
            )
            session.add(log_entry)
            session.commit()
            return {
                "success": True,
                "user_id": user_id,
                "feedback_logged": True,
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def get_feedback_stats(self, user_id=None):
        session = self.Session()
        try:
            query = session.query(SystemLog).filter(SystemLog.log_type == "user_feedback")
            if user_id:
                query = query.filter(SystemLog.log_content.contains(user_id))
            results = query.all()
            total_count = len(results)
            satisfaction_scores = []
            suggestions = []
            for row in results:
                try:
                    content = json.loads(row.log_content)
                    fb = content.get("feedback", {})
                    if "satisfaction" in fb:
                        satisfaction_scores.append(fb["satisfaction"])
                    if "suggestion" in fb:
                        suggestions.append(fb["suggestion"])
                except (json.JSONDecodeError, TypeError):
                    pass
            avg_satisfaction = None
            if satisfaction_scores:
                avg_satisfaction = round(sum(satisfaction_scores) / len(satisfaction_scores), 2)
            return {
                "total_feedback_count": total_count,
                "average_satisfaction": avg_satisfaction,
                "satisfaction_count": len(satisfaction_scores),
                "suggestion_count": len(suggestions),
            }
        finally:
            session.close()

    def list_users(self, limit=100):
        session = self.Session()
        try:
            query = session.query(UserPreference).limit(limit)
            results = query.all()
            users = []
            for row in results:
                users.append({
                    "id": row.id,
                    "user_id": row.user_id,
                    "gender_focus": row.gender_focus,
                    "category_focus": row.category_focus,
                    "heat_preference": row.heat_preference,
                    "push_frequency": row.push_frequency,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
            return users
        finally:
            session.close()

    def update_user_preference(self, user_id, updates):
        session = self.Session()
        try:
            pref = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            if not pref:
                return {"success": False, "error": "User preference not found"}
            allowed_fields = [
                "gender_focus", "category_focus", "heat_preference",
                "uniqueness_threshold", "push_channels", "push_frequency",
            ]
            updated_fields = []
            for field in allowed_fields:
                if field in updates:
                    setattr(pref, field, updates[field])
                    updated_fields.append(field)
            pref.updated_at = datetime.now()
            session.commit()
            return {
                "success": True,
                "updated_fields": updated_fields,
                "user_id": user_id,
            }
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()
