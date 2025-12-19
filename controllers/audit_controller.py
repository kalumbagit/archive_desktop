

# controllers/audit_controller.py
from database.db_manager import DatabaseManager
from models.audit_log import AuditLog
import json

class AuditController:
    def __init__(self, user, db: DatabaseManager):
        self.user = user
        self.db = db

    def log_action(self, action, entity_type, entity_id, details=None):
        """Log an action in audit trail"""
        session = self.db.get_session()
        try:
            log = AuditLog(
                user_id=self.user.id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=json.dumps(details) if isinstance(details, dict) else details
            )
            
            session.add(log)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_logs(self, entity_type=None, entity_id=None, limit=100):
        """Get audit logs"""
        session = self.db.get_session()
        try:
            query = session.query(AuditLog).filter(AuditLog.user_id == self.user.id)
            
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            
            if entity_id:
                query = query.filter(AuditLog.entity_id == entity_id)
            
            logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            return logs
        finally:
            session.close()