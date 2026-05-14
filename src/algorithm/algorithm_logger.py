import json
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from src.common.database import engine, SystemLog


class AlgorithmLogger:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def log_rule_execution(self, rule_name, input_count, output_count, duration):
        session = self.Session()
        try:
            log_content = json.dumps({
                "rule_name": rule_name,
                "input_count": input_count,
                "output_count": output_count,
                "duration": duration,
            }, ensure_ascii=False)
            log_entry = SystemLog(
                log_type="rule_execution",
                log_content=log_content,
                status="success",
            )
            session.add(log_entry)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def log_scoring_result(self, product_id, scores):
        session = self.Session()
        try:
            log_content = json.dumps({
                "product_id": product_id,
                "scores": scores,
            }, ensure_ascii=False)
            log_entry = SystemLog(
                log_type="scoring_result",
                log_content=log_content,
                status="success",
            )
            session.add(log_entry)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def log_error(self, rule_name, error_msg):
        session = self.Session()
        try:
            log_content = json.dumps({
                "rule_name": rule_name,
                "error_msg": error_msg,
            }, ensure_ascii=False)
            log_entry = SystemLog(
                log_type="error",
                log_content=log_content,
                status="error",
            )
            session.add(log_entry)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_logs(self, log_type=None, limit=100):
        session = self.Session()
        try:
            query = session.query(SystemLog)
            if log_type:
                query = query.filter(SystemLog.log_type == log_type)
            query = query.order_by(SystemLog.created_at.desc())
            query = query.limit(limit)
            results = query.all()
            logs = []
            for row in results:
                logs.append({
                    "id": row.id,
                    "log_type": row.log_type,
                    "log_content": row.log_content,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
            return logs
        finally:
            session.close()
