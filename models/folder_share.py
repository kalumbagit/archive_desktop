# models/folder_share.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db_manager import Base
from utils.enums import  SharePermission



class FolderShare(Base):
    __tablename__ = 'folder_shares'
    
    id = Column(Integer, primary_key=True)
    
    # Relations
    folder_id = Column(Integer, ForeignKey('folders.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Permission accordée
    permission = Column(SQLEnum(SharePermission), 
                       default=SharePermission.READ, 
                       nullable=False)
    
    # Qui a partagé
    shared_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    folder = relationship("Folder", back_populates="shared_with")
    user = relationship("User", foreign_keys=[user_id])
    sharer = relationship("User", foreign_keys=[shared_by])
    
    def __repr__(self):
        return f"<FolderShare(folder_id={self.folder_id}, user_id={self.user_id}, permission='{self.permission.value}')>"