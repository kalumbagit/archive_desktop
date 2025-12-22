# controllers/folder_controller.py
from database.db_manager import DatabaseManager
from models.folder import Folder
from models.file import File
from controllers.audit_controller import AuditController
from sqlalchemy import or_, func
from sqlalchemy.orm import selectinload
import os
import shutil

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
        """Get all root folders (no parent) and load all subfolders recursively"""
        session = self.db.get_session()
        try:
            folders = (
                session.query(Folder)
                .options(
                    selectinload(Folder.subfolders),
                    selectinload(Folder.owner) # ✅ Charger l'utilisateur lié
                    )
                .filter(
                    Folder.parent_id.is_(None),
                    Folder.owner_id == self.user.id
                )
                .all()
            )

            # Charger récursivement tous les sous-dossiers
            for folder in folders:
                self._load_all_subfolders(folder, session)

            # Détacher les objets pour éviter DetachedInstanceError
            session.expunge_all()
            return folders
        finally:
            session.close()

    def _load_all_subfolders(self, folder, session):
        """Forcer le chargement récursif de tous les sous-dossiers"""
        # Accéder à folder.subfolders pour déclencher le chargement
        for sub in folder.subfolders:
            # Charger aussi les sous-niveaux
            self._load_all_subfolders(sub, session)

    def get_folder_by_id(self, folder_id):
        """Get folder by ID"""
        session = self.db.get_session()
        try:
            folder = (
                session.query(Folder)
                .options(
                    selectinload(Folder.subfolders),
                    selectinload(Folder.owner) # ✅ Charger l'utilisateur lié
                    )
                .filter(Folder.id == folder_id)
                .first()
            )
            if folder:
                self._load_all_subfolders(folder, session)
                session.expunge_all()
            return folder
        finally:
            session.close()
    
    def update_folder(self, folder_id, **kwargs):
        """Update folder properties"""
        session = self.db.get_session()
        try:
            folder = (
                session.query(Folder)
                .options(
                    selectinload(Folder.subfolders),
                    selectinload(Folder.owner) # ✅ Charger l'utilisateur lié
                )
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
        """
        Delete folder and ALL its contents recursively:
        - All subfolders (at any level)
        - All files in this folder and all subfolders
        - Physical files from disk
        """
        session = self.db.get_session()
        try:
            # Récupérer le dossier avec tous ses sous-dossiers et fichiers
            folder = (
                session.query(Folder)
                .options(
                    selectinload(Folder.subfolders),
                    selectinload(Folder.files),
                    selectinload(Folder.owner) # ✅ Charger l'utilisateur lié
                )
                .filter(Folder.id == folder_id)
                .first()
            )
            
            if not folder:
                return False, "Dossier non trouvé"
            
            folder_name = folder.name
            
            # Collecter tous les fichiers à supprimer (récursivement)
            files_to_delete = []
            self._collect_all_files(folder, files_to_delete, session)
            
            # Supprimer les fichiers physiques du disque
            deleted_files_count = 0
            failed_files = []
            for file in files_to_delete:
                try:
                    if os.path.exists(file.file_path):
                        os.remove(file.file_path)
                        deleted_files_count += 1
                except Exception as e:
                    failed_files.append(f"{file.name}: {str(e)}")
            
            # Logger l'action AVANT la suppression
            self.audit.log_action('DELETE', 'FOLDER', folder_id, 
                                f"Suppression du dossier: {folder_name} "
                                f"({deleted_files_count} fichiers supprimés)")
            
            # Supprimer le dossier de la base de données
            # Grâce au CASCADE, tous les sous-dossiers et fichiers seront supprimés automatiquement
            session.delete(folder)
            session.commit()
            
            # Message de résultat
            message = f"Dossier '{folder_name}' supprimé avec succès"
            if deleted_files_count > 0:
                message += f"\n{deleted_files_count} fichier(s) supprimé(s)"
            if failed_files:
                message += f"\n\nAvertissement: {len(failed_files)} fichier(s) n'ont pas pu être supprimés du disque:\n"
                message += "\n".join(failed_files[:3])
                if len(failed_files) > 3:
                    message += f"\n... et {len(failed_files) - 3} autre(s)"
            
            return True, message
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la suppression: {str(e)}"
        finally:
            session.close()
    
    def _collect_all_files(self, folder, files_list, session):
        """
        Collecter récursivement tous les fichiers d'un dossier et de ses sous-dossiers
        """
        # Ajouter les fichiers du dossier actuel
        for file in folder.files:
            files_list.append(file)
        
        # Récursivement pour tous les sous-dossiers
        for subfolder in folder.subfolders:
            # Charger les fichiers du sous-dossier
            session.refresh(subfolder)
            self._collect_all_files(subfolder, files_list, session)
    
    def search_folders(self, query=None, year=None, theme=None, sector=None):
        session = self.db.get_session()
        try:
            filters = [Folder.owner_id == self.user.id]
            db_type = self.db.get_db_type()

            if query:
                if db_type == "sqlite":
                    filters.append(or_(
                        func.lower(Folder.name).like(f"%{query.lower()}%"),
                        func.lower(Folder.description).like(f"%{query.lower()}%")
                    ))
                else:
                    filters.append(or_(
                        Folder.name.ilike(f"%{query}%"),
                        Folder.description.ilike(f"%{query}%")
                    ))

            if year:
                filters.append(Folder.year == year)

            if theme:
                if db_type == "sqlite":
                    filters.append(func.lower(Folder.theme).like(f"%{theme.lower()}%"))
                else:
                    filters.append(Folder.theme.ilike(f"%{theme}%"))

            if sector:
                if db_type == "sqlite":
                    filters.append(func.lower(Folder.sector).like(f"%{sector.lower()}%"))
                else:
                    filters.append(Folder.sector.ilike(f"%{sector}%"))

            folders = (
                session.query(Folder)
                .options(
                    selectinload(Folder.subfolders),
                    selectinload(Folder.owner) # ✅ Charger l'utilisateur lié
                )
                .filter(*filters)
                .all()
            )

            for folder in folders:
                self._load_all_subfolders(folder, session)

            session.expunge_all()
            return folders
        finally:
            session.close()