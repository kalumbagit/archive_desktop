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
            base_path = Path(self.settings.get('storage.base_path', 'storage/files'))
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Create destination path
            file_name = Path(source_path).name
            dest_path = base_path / str(folder_id) / file_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Get file info
            file_size = os.path.getsize(dest_path)
            
            # Get MIME type using python-magic
            try:
                mime = magic.Magic(mime=True)
                mime_type = mime.from_file(str(dest_path))
            except Exception as e:
                print(f"Avertissement: Impossible de détecter le MIME type: {e}")
                mime_type = 'application/octet-stream'
            
            # Get file extension (sans le point)
            file_extension = Path(file_name).suffix[1:] if Path(file_name).suffix else ''
            
            # Create database entry
            file = File(
                name=file_name,
                file_path=str(dest_path),
                file_type=file_extension,
                file_size=file_size,
                mime_type=mime_type,
                folder_id=folder_id,
                uploaded_by=self.user.id
            )
            
            session.add(file)
            session.commit()
            
            self.audit.log_action('CREATE', 'FILE', file.id, 
                                f"Ajout du fichier: {file_name}")
            
            # Détacher l'objet pour éviter DetachedInstanceError
            session.expunge(file)
            
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
            
            # Détacher les objets pour éviter DetachedInstanceError
            session.expunge_all()
            
            return files
        finally:
            session.close()
    
    def get_file_by_id(self, file_id):
        """Get file by ID"""
        session = self.db.get_session()
        try:
            file = session.query(File).filter(File.id == file_id).first()
            
            if file:
                session.expunge(file)
            
            return file
        finally:
            session.close()
    
    def delete_file(self, file_id):
        """Delete file"""
        session = self.db.get_session()
        try:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False, "Fichier non trouvé"
            
            file_name = file.name
            file_path = file.file_path
            
            # Delete from database first
            session.delete(file)
            session.commit()
            
            # Log action
            self.audit.log_action('DELETE', 'FILE', file_id, 
                                f"Suppression du fichier: {file_name}")
            
            # Delete physical file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Avertissement: Impossible de supprimer le fichier physique: {e}")
            
            return True, "Fichier supprimé avec succès"
            
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
            
            if not os.path.exists(file.file_path):
                return False, "Le fichier source n'existe plus sur le disque"
            
            # Copy file to destination
            shutil.copy2(file.file_path, destination)
            
            self.audit.log_action('DOWNLOAD', 'FILE', file_id, 
                                f"Téléchargement du fichier: {file.name}")
            
            return True, "Fichier téléchargé avec succès"
            
        except Exception as e:
            return False, str(e)
        finally:
            session.close()
    
    def update_file(self, file_id, **kwargs):
        """Update file metadata"""
        session = self.db.get_session()
        try:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False, "Fichier non trouvé"
            
            # Update allowed fields
            allowed_fields = ['name', 'file_type']
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(file, key):
                    setattr(file, key, value)
            
            session.commit()
            
            self.audit.log_action('UPDATE', 'FILE', file_id, 
                                f"Modification du fichier: {file.name}")
            
            session.expunge(file)
            return True, file
            
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def search_files(self, query=None, file_type=None, folder_id=None):
        """Search files with filters"""
        session = self.db.get_session()
        try:
            from sqlalchemy import or_, func
            
            filters = []
            
            if query:
                db_type = self.db.get_db_type()
                if db_type == "sqlite":
                    filters.append(func.lower(File.name).like(f"%{query.lower()}%"))
                else:
                    filters.append(File.name.ilike(f"%{query}%"))
            
            if file_type:
                filters.append(File.file_type == file_type)
            
            if folder_id:
                filters.append(File.folder_id == folder_id)
            
            files = session.query(File).filter(*filters).all()
            
            session.expunge_all()
            return files
            
        finally:
            session.close()
    
    def get_file_stats(self, folder_id=None):
        """Get statistics about files"""
        session = self.db.get_session()
        try:
            from sqlalchemy import func
            
            query = session.query(
                func.count(File.id).label('total_files'),
                func.sum(File.file_size).label('total_size'),
                func.count(func.distinct(File.file_type)).label('file_types_count')
            )
            
            if folder_id:
                query = query.filter(File.folder_id == folder_id)
            
            result = query.first()
            
            return {
                'total_files': result.total_files or 0,
                'total_size': result.total_size or 0,
                'file_types_count': result.file_types_count or 0
            }
            
        finally:
            session.close()