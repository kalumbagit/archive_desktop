


# models/folder.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db_manager import Base

class Folder(Base):
    __tablename__ = 'folders'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=True)
    theme = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)
    description = Column(String(500))
    parent_id = Column(Integer, ForeignKey('folders.id'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship('User', back_populates='folders')
    parent = relationship('Folder', remote_side=[id], backref='subfolders')
    files = relationship('File', back_populates='folder', cascade='all, delete-orphan')