# models/file.py
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from database.db_manager import Base

class File(Base):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Relations avec CASCADE
    folder_id = Column(Integer, ForeignKey('folders.id', ondelete='CASCADE'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    folder = relationship("Folder", back_populates="files")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', folder_id={self.folder_id})>"