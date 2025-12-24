# config/settings.py
import json
from pathlib import Path
from typing import Any
import copy

class Settings:
    """
    Gestionnaire de configuration de l'application
    Utilise le pattern Singleton pour assurer une instance unique
    """
    _instance = None
    _config_file = Path.home() / '.archive_manager' / 'config.json'
    
    DEFAULT_SETTINGS = {
        'database': {
            'type': 'sqlite',
            'path': str(Path.home() / '.archive_manager' / 'archives.db'),
            'host': 'localhost',
            'port': 5432,
            'user': '',
            'password': '',
            'database': ''
        },
        'storage': {
            'base_path': str(Path.home() / 'Archives'),
            'cloud_enabled': False,
            'cloud_backup_enabled': False,
            'cloud_type': 'aws_s3',
            'cloud_config': {
                'aws_s3': {
                    'access_key': '',
                    'secret_key': '',
                    'bucket_name': '',
                    'region': 'us-east-1'
                },
                'azure': {
                    'account_name': '',
                    'account_key': '',
                    'container_name': ''
                },
                'google_cloud': {
                    'project_id': '',
                    'bucket_name': '',
                    'credentials_file': ''
                },
                'ftp': {
                    'host': '',
                    'port': 21,
                    'username': '',
                    'password': '',
                    'remote_path': '/'
                }
            }
        },
        'ui': {
            'theme': 'light',
            'language': 'fr'
        },
        'permissions': {
            'allow_file_deletion': True,
            'allow_folder_deletion': True,
            'require_confirmation': True
        }
    }
    
    def __new__(cls):
        """Implémentation du pattern Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialisation (appelée à chaque Settings())"""
        if not self._initialized:
            self._load_settings()
            self._initialized = True
    
    def _load_settings(self):
        """Charger les paramètres depuis le fichier ou créer les paramètres par défaut"""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Fusionner avec les paramètres par défaut pour avoir les nouvelles clés
                self.settings = self._deep_merge(
                    copy.deepcopy(self.DEFAULT_SETTINGS), 
                    loaded_settings
                )
                
                # Sauvegarder si de nouvelles clés ont été ajoutées
                if self.settings != loaded_settings:
                    self.save()
                    print("⚙️  Configuration mise à jour avec de nouvelles clés")
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  Erreur lors de la lecture du fichier de configuration: {e}")
                print("   Utilisation des paramètres par défaut")
                self.settings = copy.deepcopy(self.DEFAULT_SETTINGS)
                self.save()
        else:
            print("📝 Création du fichier de configuration par défaut")
            self.settings = copy.deepcopy(self.DEFAULT_SETTINGS)
            self.save()
    
    def _deep_merge(self, default, loaded):
        """
        Fusion récursive des dictionnaires
        Les valeurs de 'loaded' écrasent celles de 'default'
        Les clés présentes uniquement dans 'default' sont ajoutées
        """
        result = copy.deepcopy(default)
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    # Fusion récursive pour les sous-dictionnaires
                    result[key] = self._deep_merge(result[key], value)
                else:
                    # Remplacement de la valeur
                    result[key] = value
            else:
                # Nouvelle clé non présente dans default
                result[key] = value
        
        return result
    
    def save(self):
        """Sauvegarder les paramètres dans le fichier"""
        try:
            # Créer le répertoire parent s'il n'existe pas
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder avec indentation pour lisibilité
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des paramètres: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """
        Récupérer une valeur par clé (supporte la notation pointée)
        
        Exemples:
            settings.get('database.type')
            settings.get('storage.cloud_config.aws_s3.bucket_name')
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """
        Définir une valeur par clé (supporte la notation pointée)
        
        Exemples:
            settings.set('database.type', 'postgresql')
            settings.set('storage.cloud_enabled', True)
        """
        keys = key.split('.')
        settings = self.settings
        
        # Naviguer jusqu'à l'avant-dernier niveau
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            elif not isinstance(settings[k], dict):
                # Si ce n'est pas un dict, on ne peut pas continuer
                print(f"⚠️  Impossible de définir {key}: {k} n'est pas un dictionnaire")
                return
            settings = settings[k]
        
        # Définir la valeur finale
        settings[keys[-1]] = value
        self.save()
    
    def reset_to_defaults(self):
        """Réinitialiser tous les paramètres aux valeurs par défaut"""
        self.settings = copy.deepcopy(self.DEFAULT_SETTINGS)
        self.save()
        print("🔄 Paramètres réinitialisés aux valeurs par défaut")
    
    def reset_section(self, section: str):
        """
        Réinitialiser une section spécifique aux valeurs par défaut
        
        Exemples:
            settings.reset_section('database')
            settings.reset_section('storage.cloud_config')
        """
        if section in self.DEFAULT_SETTINGS:
            self.settings[section] = copy.deepcopy(self.DEFAULT_SETTINGS[section])
            self.save()
            print(f"🔄 Section '{section}' réinitialisée")
        else:
            print(f"⚠️  Section '{section}' introuvable dans les paramètres par défaut")
    
    def export_settings(self, file_path: str):
        """Exporter les paramètres vers un fichier"""
        try:
            export_path = Path(file_path)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            print(f"✅ Paramètres exportés vers: {export_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'export: {e}")
            return False
    
    def import_settings(self, file_path: str):
        """Importer les paramètres depuis un fichier"""
        try:
            import_path = Path(file_path)
            if not import_path.exists():
                print(f"❌ Fichier introuvable: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Fusionner avec les paramètres par défaut
            self.settings = self._deep_merge(
                copy.deepcopy(self.DEFAULT_SETTINGS),
                imported_settings
            )
            self.save()
            print(f"✅ Paramètres importés depuis: {import_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'import: {e}")
            return False
    
    def validate(self) -> tuple[bool, list]:
        """
        Valider la cohérence des paramètres
        Retourne (is_valid, errors)
        """
        errors = []
        
        # Vérifier le type de base de données
        db_type = self.get('database.type')
        if db_type not in ['sqlite', 'postgresql', 'mysql']:
            errors.append(f"Type de base de données invalide: {db_type}")
        
        # Vérifier le chemin SQLite
        if db_type == 'sqlite':
            db_path = self.get('database.path')
            if not db_path:
                errors.append("Chemin de base de données SQLite manquant")
        
        # Vérifier les paramètres de base distante
        if db_type in ['postgresql', 'mysql']:
            for field in ['host', 'port', 'user', 'database']:
                if not self.get(f'database.{field}'):
                    errors.append(f"Paramètre de base de données manquant: {field}")
        
        # Vérifier le chemin de stockage
        storage_path = self.get('storage.base_path')
        if not storage_path:
            errors.append("Chemin de stockage manquant")
        
        # Vérifier la configuration cloud si activée
        if self.get('storage.cloud_enabled'):
            cloud_type = self.get('storage.cloud_type')
            if cloud_type == 'aws_s3':
                required = ['access_key', 'secret_key', 'bucket_name']
                for field in required:
                    if not self.get(f'storage.cloud_config.aws_s3.{field}'):
                        errors.append(f"Configuration AWS S3 incomplète: {field} manquant")
            
            elif cloud_type == 'azure':
                required = ['account_name', 'account_key', 'container_name']
                for field in required:
                    if not self.get(f'storage.cloud_config.azure.{field}'):
                        errors.append(f"Configuration Azure incomplète: {field} manquant")
            
            elif cloud_type == 'google_cloud':
                required = ['project_id', 'bucket_name']
                for field in required:
                    if not self.get(f'storage.cloud_config.google_cloud.{field}'):
                        errors.append(f"Configuration Google Cloud incomplète: {field} manquant")
            
            elif cloud_type == 'ftp':
                required = ['host', 'username']
                for field in required:
                    if not self.get(f'storage.cloud_config.ftp.{field}'):
                        errors.append(f"Configuration FTP incomplète: {field} manquant")
        
        return (len(errors) == 0, errors)
    
    def __getitem__(self, key: str) -> Any:
        """Permettre l'accès de type dictionnaire: settings['database.type']"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Permettre l'assignation de type dictionnaire: settings['database.type'] = 'sqlite'"""
        self.set(key, value)
    
    def __str__(self):
        """Représentation en chaîne des paramètres"""
        return json.dumps(self.settings, indent=2, ensure_ascii=False)
    
    def __repr__(self):
        """Représentation pour le débogage"""
        return f"<Settings(config_file='{self._config_file}')>"