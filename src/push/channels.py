import json
from datetime import datetime

from sqlalchemy.orm import Session

from src.common.database import PushRecord, UserPreference, engine


class PushChannelManager:

    def push(self, channel: str, content: dict, user_id: str) -> bool:
        channel_methods = {
            "skill_message": self.push_skill_message,
            "email": self.push_email,
            "sms": self.push_sms,
        }
        method = channel_methods.get(channel)
        if not method:
            self._record_push(user_id, content.get("push_type", ""), content, channel, "failed")
            return False
        result = method(content, user_id)
        return result

    def push_skill_message(self, content: dict, user_id: str) -> bool:
        try:
            self._record_push(
                user_id, content.get("push_type", ""), content, "skill_message", "success"
            )
            return True
        except Exception:
            self._record_push(
                user_id, content.get("push_type", ""), content, "skill_message", "failed"
            )
            return False

    def push_email(self, content: dict, user_id: str) -> bool:
        try:
            self._record_push(
                user_id, content.get("push_type", ""), content, "email", "success"
            )
            return True
        except Exception:
            self._record_push(
                user_id, content.get("push_type", ""), content, "email", "failed"
            )
            return False

    def push_sms(self, content: dict, user_id: str) -> bool:
        try:
            self._record_push(
                user_id, content.get("push_type", ""), content, "sms", "success"
            )
            return True
        except Exception:
            self._record_push(
                user_id, content.get("push_type", ""), content, "sms", "failed"
            )
            return False

    def _get_user_channel_preference(self, user_id: str) -> list:
        session = Session(engine)
        try:
            preference = (
                session.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )
            if preference and preference.push_channels:
                channels = [
                    ch.strip()
                    for ch in preference.push_channels.split(",")
                    if ch.strip()
                ]
                return channels
            return ["skill_message"]
        finally:
            session.close()

    def _record_push(
        self,
        user_id: str,
        push_type: str,
        content: dict,
        channel: str,
        status: str,
    ):
        session = Session(engine)
        try:
            record = PushRecord(
                user_id=user_id,
                push_type=push_type,
                push_content=json.dumps(content, ensure_ascii=False),
                push_channel=channel,
                push_status=status,
                created_at=datetime.now(),
            )
            session.add(record)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
