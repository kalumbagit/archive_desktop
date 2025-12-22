# models/folder.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
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
    description = Column(Text, nullable=True)
    
    # Relations
    parent_id = Column(Integer, ForeignKey('folders.id', ondelete='CASCADE'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships avec cascade
    owner = relationship("User", back_populates="folders")
    
    # Relation parent (Many-to-One)
    parent = relationship(
        "Folder",
        remote_side=[id],
        back_populates="subfolders"
    )
    
    # Relation enfants (One-to-Many) avec cascade
    subfolders = relationship(
        "Folder",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    
    # Cascade pour les fichiers : si un dossier est supprimé, tous ses fichiers le sont aussi
    files = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', year={self.year})>"