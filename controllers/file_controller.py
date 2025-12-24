# controllers/file_controller.py
from database.db_manager import DatabaseManager
from models.file import File
from controllers.audit_controller import AuditController
from config.settings import Settings
import shutil
import os
from pathlib import Path
import magic
import threading

class FileController:
    def __init__(self, user, db: DatabaseManager):
        self.user = user
        self.db = db
        self.audit = AuditController(user, db)
        self.settings = Settings()
    
    def _upload_to_cloud(self, file_path, file_name, folder_id):
        """
        Upload un fichier vers le cloud en arrière-plan
        Cette méthode s'exécute dans un thread séparé
        """
        try:
            # Vérifier si le cloud est activé
            if not self.settings.get('storage.cloud_enabled'):
                return False, "Cloud non activé"
            
            cloud_type = self.settings.get('storage.cloud_type')
            cloud_config = self.settings.get(f'storage.cloud_config.{cloud_type}', {})
            
            # Chemin distant avec structure: folder_id/filename
            remote_path = f"folder_{folder_id}/{file_name}"
            
            if cloud_type == 'aws_s3':
                return self._upload_to_s3(file_path, remote_path, cloud_config)
            elif cloud_type == 'azure':
                return self._upload_to_azure(file_path, remote_path, cloud_config)
            elif cloud_type == 'google_cloud':
                return self._upload_to_google_cloud(file_path, remote_path, cloud_config)
            elif cloud_type == 'ftp':
                return self._upload_to_ftp(file_path, remote_path, cloud_config)
            else:
                return False, f"Type de cloud non supporté: {cloud_type}"
                
        except Exception as e:
            print(f"❌ Erreur upload cloud: {e}")
            return False, str(e)
    
    def _upload_to_s3(self, file_path, remote_path, config):
        """Upload vers AWS S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('access_key'),
                aws_secret_access_key=config.get('secret_key'),
                region_name=config.get('region', 'us-east-1')
            )
            
            bucket_name = config.get('bucket_name')
            s3_client.upload_file(file_path, bucket_name, remote_path)
            
            print(f"✅ Fichier uploadé vers S3: s3://{bucket_name}/{remote_path}")
            return True, f"s3://{bucket_name}/{remote_path}"
            
        except ImportError:
            return False, "boto3 non installé. pip install boto3"
        except ClientError as e:
            return False, f"Erreur S3: {str(e)}"
        except Exception as e:
            return False, str(e)
    
    def _upload_to_azure(self, file_path, remote_path, config):
        """Upload vers Azure Blob Storage"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={config.get('account_name')};AccountKey={config.get('account_key')};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            container_name = config.get('container_name')
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=remote_path
            )
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"✅ Fichier uploadé vers Azure: {container_name}/{remote_path}")
            return True, f"azure://{container_name}/{remote_path}"
            
        except ImportError:
            return False, "azure-storage-blob non installé. pip install azure-storage-blob"
        except Exception as e:
            return False, str(e)
    
    def _upload_to_google_cloud(self, file_path, remote_path, config):
        """Upload vers Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            # Définir les credentials si fournis
            credentials_file = config.get('credentials_file')
            if credentials_file and os.path.exists(credentials_file):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            
            client = storage.Client(project=config.get('project_id'))
            bucket = client.bucket(config.get('bucket_name'))
            blob = bucket.blob(remote_path)
            
            blob.upload_from_filename(file_path)
            
            print(f"✅ Fichier uploadé vers Google Cloud: gs://{config.get('bucket_name')}/{remote_path}")
            return True, f"gs://{config.get('bucket_name')}/{remote_path}"
            
        except ImportError:
            return False, "google-cloud-storage non installé. pip install google-cloud-storage"
        except Exception as e:
            return False, str(e)
    
    def _upload_to_ftp(self, file_path, remote_path, config):
        """Upload vers serveur FTP"""
        try:
            from ftplib import FTP
            
            ftp = FTP()
            ftp.connect(config.get('host'), int(config.get('port', 21)))
            ftp.login(config.get('username'), config.get('password'))
            
            # Créer les répertoires si nécessaire
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                try:
                    ftp.cwd(config.get('remote_path', '/'))
                    for folder in remote_dir.split('/'):
                        if folder:
                            try:
                                ftp.mkd(folder)
                            except:
                                pass  # Dossier existe déjà
                            ftp.cwd(folder)
                except:
                    pass
            
            # Upload du fichier
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(remote_path)}', file)
            
            ftp.quit()
            
            print(f"✅ Fichier uploadé vers FTP: {config.get('host')}/{remote_path}")
            return True, f"ftp://{config.get('host')}/{remote_path}"
            
        except Exception as e:
            return False, str(e)
    
    def _delete_from_cloud(self, file_name, folder_id):
        """
        Supprimer un fichier du cloud
        """
        try:
            if not self.settings.get('storage.cloud_enabled'):
                return True, "Cloud non activé"
            
            cloud_type = self.settings.get('storage.cloud_type')
            cloud_config = self.settings.get(f'storage.cloud_config.{cloud_type}', {})
            remote_path = f"folder_{folder_id}/{file_name}"
            
            if cloud_type == 'aws_s3':
                return self._delete_from_s3(remote_path, cloud_config)
            elif cloud_type == 'azure':
                return self._delete_from_azure(remote_path, cloud_config)
            elif cloud_type == 'google_cloud':
                return self._delete_from_google_cloud(remote_path, cloud_config)
            elif cloud_type == 'ftp':
                return self._delete_from_ftp(remote_path, cloud_config)
            
            return True, "Suppression cloud ignorée"
            
        except Exception as e:
            print(f"⚠️  Erreur suppression cloud: {e}")
            return False, str(e)
    
    def _delete_from_s3(self, remote_path, config):
        """Supprimer de AWS S3"""
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('access_key'),
                aws_secret_access_key=config.get('secret_key'),
                region_name=config.get('region', 'us-east-1')
            )
            
            s3_client.delete_object(
                Bucket=config.get('bucket_name'),
                Key=remote_path
            )
            
            print(f"✅ Fichier supprimé de S3: {remote_path}")
            return True, "Supprimé de S3"
        except Exception as e:
            return False, str(e)
    
    def _delete_from_azure(self, remote_path, config):
        """Supprimer de Azure"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={config.get('account_name')};AccountKey={config.get('account_key')};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            blob_client = blob_service_client.get_blob_client(
                container=config.get('container_name'),
                blob=remote_path
            )
            
            blob_client.delete_blob()
            
            print(f"✅ Fichier supprimé d'Azure: {remote_path}")
            return True, "Supprimé d'Azure"
        except Exception as e:
            return False, str(e)
    
    def _delete_from_google_cloud(self, remote_path, config):
        """Supprimer de Google Cloud"""
        try:
            from google.cloud import storage
            
            credentials_file = config.get('credentials_file')
            if credentials_file and os.path.exists(credentials_file):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            
            client = storage.Client(project=config.get('project_id'))
            bucket = client.bucket(config.get('bucket_name'))
            blob = bucket.blob(remote_path)
            
            blob.delete()
            
            print(f"✅ Fichier supprimé de Google Cloud: {remote_path}")
            return True, "Supprimé de Google Cloud"
        except Exception as e:
            return False, str(e)
    
    def _delete_from_ftp(self, remote_path, config):
        """Supprimer du FTP"""
        try:
            from ftplib import FTP
            
            ftp = FTP()
            ftp.connect(config.get('host'), int(config.get('port', 21)))
            ftp.login(config.get('username'), config.get('password'))
            
            ftp.cwd(config.get('remote_path', '/'))
            ftp.delete(remote_path)
            ftp.quit()
            
            print(f"✅ Fichier supprimé du FTP: {remote_path}")
            return True, "Supprimé du FTP"
        except Exception as e:
            return False, str(e)
    
    def add_file(self, source_path, folder_id):
        """Add file to archive (local + cloud si activé)"""
        session = self.db.get_session()
        try:
            # Get storage base path
            base_path = Path(self.settings.get('storage.base_path', 'storage/files'))
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Create destination path
            file_name = Path(source_path).name
            dest_path = base_path / str(folder_id) / file_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file localement
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
            
            # Upload vers le cloud si activé
            if self.settings.get('storage.cloud_enabled') or \
               self.settings.get('storage.cloud_backup_enabled'):
                
                # Lancer l'upload dans un thread séparé pour ne pas bloquer
                upload_thread = threading.Thread(
                    target=self._upload_to_cloud,
                    args=(str(dest_path), file_name, folder_id),
                    daemon=True
                )
                upload_thread.start()
                
                print(f"☁️  Upload cloud en cours pour: {file_name}")
            
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
        """Delete file (local + cloud si activé)"""
        session = self.db.get_session()
        try:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False, "Fichier non trouvé"
            
            file_name = file.name
            file_path = file.file_path
            folder_id = file.folder_id
            
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
                    print(f"✅ Fichier local supprimé: {file_path}")
                except Exception as e:
                    print(f"⚠️  Impossible de supprimer le fichier local: {e}")
            
            # Delete from cloud if enabled
            if self.settings.get('storage.cloud_enabled') or \
               self.settings.get('storage.cloud_backup_enabled'):
                
                # Lancer la suppression cloud dans un thread
                delete_thread = threading.Thread(
                    target=self._delete_from_cloud,
                    args=(file_name, folder_id),
                    daemon=True
                )
                delete_thread.start()
                
                print(f"☁️  Suppression cloud en cours pour: {file_name}")
            
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
    
    def get_cloud_status(self):
        """Obtenir le statut de la configuration cloud"""
        return {
            'enabled': self.settings.get('storage.cloud_enabled', False),
            'backup_enabled': self.settings.get('storage.cloud_backup_enabled', False),
            'type': self.settings.get('storage.cloud_type', 'aws_s3'),
            'configured': bool(self.settings.get('storage.cloud_enabled'))
        }