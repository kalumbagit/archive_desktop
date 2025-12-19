
# controllers/file_controller.py
from database.db_manager import DatabaseManager
from models.file import File
from controllers.audit_controller import AuditController
from config.settings import Settings
import shutil
import os
from pathlib import Path
import magic

class FileController:
    def __init__(self, user, db: DatabaseManager):
        self.user = user
        self.db = db
        self.audit = AuditController(user, db)
        self.settings = Settings()
    
    def add_file(self, source_path, folder_id):
        """Add file to archive"""
        session = self.db.get_session()
        try:
            # Get storage base path
            base_path = Path(self.settings.get('storage.base_path'))
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Create destination path
            file_name = Path(source_path).name
            dest_path = base_path / str(folder_id) / file_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Get file info
            file_size = os.path.getsize(dest_path)
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(str(dest_path))
            
            # Create database entry
            file = File(
                name=file_name,
                file_path=str(dest_path),
                file_type=Path(file_name).suffix[1:],
                file_size=file_size,
                mime_type=mime_type,
                folder_id=folder_id,
                uploaded_by=self.user.id
            )
            
            session.add(file)
            session.commit()
            
            self.audit.log_action('CREATE', 'FILE', file.id, 
                                f"Ajout du fichier: {file_name}")
            
            return True, file
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def get_files_in_folder(self, folder_id):
        """Get all files in a folder"""
        session = self.db.get_session()
        try:
            files = session.query(File).filter(File.folder_id == folder_id).all()
            return files
        finally:
            session.close()
    
    def delete_file(self, file_id):
        """Delete file"""
        session = self.db.get_session()
        try:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False, "Fichier non trouvé"
            
            # Delete physical file
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
            
            file_name = file.name
            session.delete(file)
            session.commit()
            
            self.audit.log_action('DELETE', 'FILE', file_id, 
                                f"Suppression du fichier: {file_name}")
            
            return True, "Fichier supprimé"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def download_file(self, file_id, destination):
        """Download/export file"""
        session = self.db.get_session()
        try:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False, "Fichier non trouvé"
            
            shutil.copy2(file.file_path, destination)
            
            self.audit.log_action('DOWNLOAD', 'FILE', file_id, 
                                f"Téléchargement du fichier: {file.name}")
            
            return True, "Fichier téléchargé"
        except Exception as e:
            return False, str(e)
        finally:
            session.close()
