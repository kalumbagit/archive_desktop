

# models/audit_log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db_manager import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, DOWNLOAD, VIEW
    entity_type = Column(String(50), nullable=False)  # USER, FOLDER, FILE
    entity_id = Column(Integer, nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='audit_logs')