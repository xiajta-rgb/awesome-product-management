import json
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from src.algorithm.algorithm_logger import AlgorithmLogger
from src.algorithm.rule5_optimizer import AlgorithmOptimizer
from src.common.database import engine, SystemLog


class AlgorithmManager:
    def __init__(self):
        self.optimizer = AlgorithmOptimizer()
        self.logger = AlgorithmLogger()
        self.Session = sessionmaker(bind=engine)

    def view_algorithm_logs(self, log_type=None, limit=100):
        return self.logger.get_logs(log_type=log_type, limit=limit)

    def trigger_optimization(self, market_data=None):
        try:
            if market_data is None:
                market_data = {}
            current_weights = dict(self.optimizer.DEFAULT_WEIGHTS)
            optimized_weights = self.optimizer.optimize_weights(current_weights, market_data)
            log_content = json.dumps({
                "action": "manual_optimization",
                "previous_weights": current_weights,
                "optimized_weights": optimized_weights,
                "market_data": market_data,
            }, ensure_ascii=False)
            session = self.Session()
            try:
                log_entry = SystemLog(
                    log_type="optimization",
                    log_content=log_content,
                    status="success",
                )
                session.add(log_entry)
                session.commit()
            finally:
                session.close()
            return {
                "success": True,
                "previous_weights": current_weights,
                "optimized_weights": optimized_weights,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def adjust_algorithm_logic(self, feedback):
        try:
            current_weights = dict(self.optimizer.DEFAULT_WEIGHTS)
            adjusted_weights = self._apply_feedback_adjustment(current_weights, feedback)
            log_content = json.dumps({
                "action": "feedback_adjustment",
                "feedback": feedback,
                "previous_weights": current_weights,
                "adjusted_weights": adjusted_weights,
            }, ensure_ascii=False)
            session = self.Session()
            try:
                log_entry = SystemLog(
                    log_type="feedback_adjustment",
                    log_content=log_content,
                    status="success",
                )
                session.add(log_entry)
                session.commit()
            finally:
                session.close()
            return {
                "success": True,
                "previous_weights": current_weights,
                "adjusted_weights": adjusted_weights,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_current_weights(self):
        return dict(self.optimizer.DEFAULT_WEIGHTS)

    def get_optimization_history(self, limit=10):
        session = self.Session()
        try:
            query = session.query(SystemLog).filter(
                SystemLog.log_type.in_(["optimization", "feedback_adjustment"])
            )
            query = query.order_by(SystemLog.created_at.desc())
            query = query.limit(limit)
            results = query.all()
            history = []
            for row in results:
                entry = {
                    "id": row.id,
                    "log_type": row.log_type,
                    "log_content": row.log_content,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                history.append(entry)
            return history
        finally:
            session.close()

    def _apply_feedback_adjustment(self, weights, feedback):
        adjusted = dict(weights)
        satisfaction = feedback.get("satisfaction")
        if satisfaction is not None:
            if satisfaction < 0.3:
                adjusted["trend"] = adjusted.get("trend", 0.25) + 0.05
                adjusted["sales"] = adjusted.get("sales", 0.3) - 0.03
            elif satisfaction < 0.6:
                adjusted["trend"] = adjusted.get("trend", 0.25) + 0.02
                adjusted["sales"] = adjusted.get("sales", 0.3) - 0.01
        category_feedback = feedback.get("category_feedback")
        if category_feedback:
            if category_feedback.get("trend_relevance") == "low":
                adjusted["trend"] = adjusted.get("trend", 0.25) - 0.03
                adjusted["sales"] = adjusted.get("sales", 0.3) + 0.02
            elif category_feedback.get("trend_relevance") == "high":
                adjusted["trend"] = adjusted.get("trend", 0.25) + 0.03
                adjusted["sales"] = adjusted.get("sales", 0.3) - 0.02
        weight_adjustments = feedback.get("weight_adjustments")
        if weight_adjustments:
            for key, delta in weight_adjustments.items():
                if key in adjusted:
                    adjusted[key] = adjusted[key] + delta
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: round(v / total, 4) for k, v in adjusted.items()}
        return adjusted
