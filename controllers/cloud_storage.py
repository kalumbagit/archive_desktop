# services/cloud_storage.py
"""Service de gestion du stockage cloud"""
import os

class CloudStorageService:
    """Service de connexion et upload vers le cloud"""
    
    @staticmethod
    def test_aws_s3_connection(access_key, secret_key, bucket_name, region):
        """Tester la connexion à AWS S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            # Tester la connexion en listant les buckets
            s3_client.head_bucket(Bucket=bucket_name)
            return True, "Connexion AWS S3 réussie"
            
        except ImportError:
            return False, "Bibliothèque boto3 non installée. Installez avec: pip install boto3"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403':
                return False, "Accès refusé. Vérifiez vos clés d'accès"
            elif error_code == '404':
                return False, f"Bucket '{bucket_name}' introuvable"
            else:
                return False, f"Erreur AWS: {str(e)}"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def test_azure_connection(account_name, account_key, container_name):
        """Tester la connexion à Azure Blob Storage"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Tester en obtenant les propriétés du container
            container_client = blob_service_client.get_container_client(container_name)
            container_client.get_container_properties()
            
            return True, "Connexion Azure réussie"
            
        except ImportError:
            return False, "Bibliothèque azure-storage-blob non installée. Installez avec: pip install azure-storage-blob"
        except Exception as e:
            return False, f"Erreur Azure: {str(e)}"
    
    @staticmethod
    def test_google_cloud_connection(project_id, bucket_name, credentials_file):
        """Tester la connexion à Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            # Définir les credentials
            if credentials_file and os.path.exists(credentials_file):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            
            client = storage.Client(project=project_id)
            bucket = client.bucket(bucket_name)
            
            # Tester en vérifiant l'existence du bucket
            if bucket.exists():
                return True, "Connexion Google Cloud réussie"
            else:
                return False, f"Bucket '{bucket_name}' introuvable"
                
        except ImportError:
            return False, "Bibliothèque google-cloud-storage non installée. Installez avec: pip install google-cloud-storage"
        except Exception as e:
            return False, f"Erreur Google Cloud: {str(e)}"
    
    @staticmethod
    def test_ftp_connection(host, port, username, password, remote_path):
        """Tester la connexion FTP"""
        try:
            from ftplib import FTP
            
            ftp = FTP()
            ftp.connect(host, port, timeout=10)
            ftp.login(username, password)
            
            # Tester en changeant de répertoire
            ftp.cwd(remote_path)
            ftp.quit()
            
            return True, "Connexion FTP réussie"
            
        except Exception as e:
            return False, f"Erreur FTP: {str(e)}"
    
    @staticmethod
    def test_connection(cloud_type, config):
        """Tester la connexion selon le type de cloud"""
        if cloud_type == 'aws_s3':
            return CloudStorageService.test_aws_s3_connection(
                config.get('access_key', ''),
                config.get('secret_key', ''),
                config.get('bucket_name', ''),
                config.get('region', 'us-east-1')
            )
        elif cloud_type == 'azure':
            return CloudStorageService.test_azure_connection(
                config.get('account_name', ''),
                config.get('account_key', ''),
                config.get('container_name', '')
            )
        elif cloud_type == 'google_cloud':
            return CloudStorageService.test_google_cloud_connection(
                config.get('project_id', ''),
                config.get('bucket_name', ''),
                config.get('credentials_file', '')
            )
        elif cloud_type == 'ftp':
            return CloudStorageService.test_ftp_connection(
                config.get('host', ''),
                int(config.get('port', 21)),
                config.get('username', ''),
                config.get('password', ''),
                config.get('remote_path', '/')
            )
        else:
            return False, f"Type de cloud non supporté: {cloud_type}"