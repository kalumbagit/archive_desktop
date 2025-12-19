# controllers/folder_controller.py
from database.db_manager import DatabaseManager
from models.folder import Folder
from controllers.audit_controller import AuditController
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

class FolderController:
    def __init__(self, user, db: DatabaseManager):
        self.user = user
        self.db = db
        self.audit = AuditController(user, db)

    def create_folder(self, name, year=None, theme=None, sector=None, 
                     description=None, parent_id=None):
        """Create a new folder"""
        session = self.db.get_session()
        try:
            folder = Folder(
                name=name,
                year=year,
                theme=theme,
                sector=sector,
                description=description,
                parent_id=parent_id,
                owner_id=self.user.id
            )
            
            session.add(folder)
            session.commit()
            
            self.audit.log_action('CREATE', 'FOLDER', folder.id, 
                                f"Création du dossier: {name}")
            
            return True, folder
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def get_root_folders(self):
        """Get all root folders (no parent)"""
        session = self.db.get_session()
        try:
            folders = session.query(Folder).options(selectinload(Folder.subfolders)).filter(
                Folder.parent_id.is_(None),
                Folder.owner_id == self.user.id
            ).all()
            return folders
        finally:
            session.close()
    
    def get_folder_by_id(self, folder_id):
        """Get folder by ID"""
        session = self.db.get_session()
        try:
            folder = session.query(Folder).filter(Folder.id == folder_id).first()
            return folder
        finally:
            session.close()
    
    def update_folder(self, folder_id, **kwargs):
        """Update folder properties"""
        session = self.db.get_session()
        try:
            folder = (
                session.query(Folder)
                .options(selectinload(Folder.subfolders))
                .filter(Folder.id == folder_id)
                .first()
                )
            if not folder:
                return False, "Dossier non trouvé"
            
            for key, value in kwargs.items():
                if hasattr(folder, key):
                    setattr(folder, key, value)
            
            session.commit()
            self.audit.log_action('UPDATE', 'FOLDER', folder_id, 
                                f"Modification du dossier")
            
            return True, folder
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def delete_folder(self, folder_id):
        """Delete folder and its contents"""
        session = self.db.get_session()
        try:
            folder = session.query(Folder).filter(Folder.id == folder_id).first()
            if not folder:
                return False, "Dossier non trouvé"
            
            folder_name = folder.name
            session.delete(folder)
            session.commit()
            
            self.audit.log_action('DELETE', 'FOLDER', folder_id, 
                                f"Suppression du dossier: {folder_name}")
            
            return True, "Dossier supprimé"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def search_folders(self, query=None, year=None, theme=None, sector=None):
        """Search folders by criteria"""
        session = self.db.get_session()
        try:
            filters = [Folder.owner_id == self.user.id]
            
            if query:
                filters.append(or_(
                    Folder.name.ilike(f'%{query}%'),
                    Folder.description.ilike(f'%{query}%')
                ))
            
            if year:
                filters.append(Folder.year == year)
            
            if theme:
                filters.append(Folder.theme.ilike(f'%{theme}%'))
            
            if sector:
                filters.append(Folder.sector.ilike(f'%{sector}%'))
            
            folders = session.query(Folder).filter(*filters).all()
            return folders
        finally:
            session.close()

