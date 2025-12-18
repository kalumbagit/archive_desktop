# controllers/search_controller.py
"""
Contrôleur de recherche pour l'application de gestion d'archives
Gère les recherches avancées de dossiers et fichiers
"""

from database.db_manager import DatabaseManager
from models.folder import Folder
from models.file import File
from sqlalchemy import or_, and_
from datetime import datetime

class SearchController:
    """Contrôleur pour les opérations de recherche avancée"""
    
    def __init__(self, user):
        """
        Initialiser le contrôleur de recherche
        
        Args:
            user: L'utilisateur courant (objet User)
        """
        self.user = user
        self.db = DatabaseManager()
    
    def search(self, 
              query=None,
              year=None,
              theme=None,
              sector=None,
              search_type='all',
              case_sensitive=False):
        """
        Recherche avancée pour dossiers et fichiers
        
        Args:
            query (str): Mot-clé de recherche
            year (int): Filtrer par année
            theme (str): Filtrer par thème
            sector (str): Filtrer par secteur
            search_type (str): 'all', 'folders', ou 'files'
            case_sensitive (bool): Recherche sensible à la casse
        
        Returns:
            dict: Dictionnaire avec les clés 'folders' et 'files'
        """
        results = {
            'folders': [],
            'files': []
        }
        
        # Rechercher dans les dossiers si demandé
        if search_type in ['all', 'folders']:
            results['folders'] = self.search_folders(
                query=query,
                year=year,
                theme=theme,
                sector=sector,
                case_sensitive=case_sensitive
            )
        
        # Rechercher dans les fichiers si demandé
        if search_type in ['all', 'files']:
            results['files'] = self.search_files(
                query=query,
                case_sensitive=case_sensitive
            )
        
        return results
    
    def search_folders(self, query=None, year=None, theme=None, 
                      sector=None, case_sensitive=False):
        """
        Rechercher des dossiers avec plusieurs critères
        
        Args:
            query (str): Mot-clé de recherche (nom ou description)
            year (int): Année du dossier
            theme (str): Thème du dossier
            sector (str): Secteur du dossier
            case_sensitive (bool): Recherche sensible à la casse
        
        Returns:
            list: Liste des dossiers trouvés
        """
        session = self.db.get_session()
        
        try:
            # Filtre de base : dossiers de l'utilisateur courant
            filters = [Folder.owner_id == self.user.id]
            
            # Ajouter le filtre de mot-clé si fourni
            if query:
                if case_sensitive:
                    filters.append(or_(
                        Folder.name.contains(query),
                        Folder.description.contains(query)
                    ))
                else:
                    filters.append(or_(
                        Folder.name.ilike(f'%{query}%'),
                        Folder.description.ilike(f'%{query}%')
                    ))
            
            # Ajouter le filtre d'année si fourni
            if year:
                filters.append(Folder.year == year)
            
            # Ajouter le filtre de thème si fourni
            if theme:
                if case_sensitive:
                    filters.append(Folder.theme.contains(theme))
                else:
                    filters.append(Folder.theme.ilike(f'%{theme}%'))
            
            # Ajouter le filtre de secteur si fourni
            if sector:
                if case_sensitive:
                    filters.append(Folder.sector.contains(sector))
                else:
                    filters.append(Folder.sector.ilike(f'%{sector}%'))
            
            # Exécuter la requête
            folders = session.query(Folder).filter(and_(*filters)).all()
            
            return folders
        
        except Exception as e:
            print(f"Erreur lors de la recherche de dossiers: {e}")
            return []
        
        finally:
            session.close()
    
    def search_files(self, query=None, case_sensitive=False, file_type=None):
        """
        Rechercher des fichiers par nom
        
        Args:
            query (str): Mot-clé de recherche dans le nom du fichier
            case_sensitive (bool): Recherche sensible à la casse
            file_type (str): Type/extension de fichier (ex: 'pdf', 'jpg')
        
        Returns:
            list: Liste des fichiers trouvés
        """
        session = self.db.get_session()
        
        try:
            # Joindre avec les dossiers pour filtrer par propriétaire
            query_obj = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id
            )
            
            # Ajouter le filtre de nom si fourni
            if query:
                if case_sensitive:
                    query_obj = query_obj.filter(File.name.contains(query))
                else:
                    query_obj = query_obj.filter(File.name.ilike(f'%{query}%'))
            
            # Ajouter le filtre de type si fourni
            if file_type:
                query_obj = query_obj.filter(File.file_type.ilike(file_type))
            
            # Exécuter la requête
            files = query_obj.all()
            
            return files
        
        except Exception as e:
            print(f"Erreur lors de la recherche de fichiers: {e}")
            return []
        
        finally:
            session.close()
    
    def search_by_file_type(self, file_type):
        """
        Rechercher tous les fichiers d'un type spécifique
        
        Args:
            file_type (str): Extension du fichier (ex: 'pdf', 'docx', 'jpg')
        
        Returns:
            list: Liste des fichiers du type spécifié
        """
        session = self.db.get_session()
        
        try:
            files = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id,
                File.file_type.ilike(file_type)
            ).all()
            
            return files
        
        except Exception as e:
            print(f"Erreur lors de la recherche par type: {e}")
            return []
        
        finally:
            session.close()
    
    def search_by_date_range(self, start_date=None, end_date=None):
        """
        Rechercher des fichiers dans une plage de dates
        
        Args:
            start_date (datetime): Date de début
            end_date (datetime): Date de fin
        
        Returns:
            list: Liste des fichiers dans la plage de dates
        """
        session = self.db.get_session()
        
        try:
            query_obj = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id
            )
            
            if start_date:
                query_obj = query_obj.filter(File.created_at >= start_date)
            
            if end_date:
                query_obj = query_obj.filter(File.created_at <= end_date)
            
            files = query_obj.order_by(File.created_at.desc()).all()
            
            return files
        
        except Exception as e:
            print(f"Erreur lors de la recherche par date: {e}")
            return []
        
        finally:
            session.close()
    
    def get_recent_files(self, limit=20):
        """
        Obtenir les fichiers récemment ajoutés
        
        Args:
            limit (int): Nombre maximum de fichiers à retourner
        
        Returns:
            list: Liste des fichiers les plus récents
        """
        session = self.db.get_session()
        
        try:
            files = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id
            ).order_by(File.created_at.desc()).limit(limit).all()
            
            return files
        
        except Exception as e:
            print(f"Erreur lors de la récupération des fichiers récents: {e}")
            return []
        
        finally:
            session.close()
    
    def get_large_files(self, min_size_mb=10, limit=20):
        """
        Obtenir les fichiers volumineux
        
        Args:
            min_size_mb (int): Taille minimale en mégaoctets
            limit (int): Nombre maximum de fichiers à retourner
        
        Returns:
            list: Liste des fichiers volumineux
        """
        session = self.db.get_session()
        
        try:
            min_size_bytes = min_size_mb * 1024 * 1024
            
            files = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id,
                File.file_size >= min_size_bytes
            ).order_by(File.file_size.desc()).limit(limit).all()
            
            return files
        
        except Exception as e:
            print(f"Erreur lors de la récupération des fichiers volumineux: {e}")
            return []
        
        finally:
            session.close()
    
    def get_files_by_folder(self, folder_id):
        """
        Obtenir tous les fichiers d'un dossier spécifique
        
        Args:
            folder_id (int): ID du dossier
        
        Returns:
            list: Liste des fichiers du dossier
        """
        session = self.db.get_session()
        
        try:
            files = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id,
                File.folder_id == folder_id
            ).all()
            
            return files
        
        except Exception as e:
            print(f"Erreur lors de la récupération des fichiers du dossier: {e}")
            return []
        
        finally:
            session.close()
    
    def get_statistics(self):
        """
        Obtenir des statistiques sur les archives de l'utilisateur
        
        Returns:
            dict: Dictionnaire contenant les statistiques
        """
        session = self.db.get_session()
        
        try:
            # Compter les dossiers
            total_folders = session.query(Folder).filter(
                Folder.owner_id == self.user.id
            ).count()
            
            # Compter les fichiers
            total_files = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id
            ).count()
            
            # Calculer la taille totale
            from sqlalchemy import func
            total_size = session.query(func.sum(File.file_size)).join(Folder).filter(
                Folder.owner_id == self.user.id
            ).scalar() or 0
            
            # Obtenir les types de fichiers les plus courants
            file_types = session.query(
                File.file_type,
                func.count(File.id).label('count')
            ).join(Folder).filter(
                Folder.owner_id == self.user.id
            ).group_by(File.file_type).order_by(func.count(File.id).desc()).limit(5).all()
            
            return {
                'total_folders': total_folders,
                'total_files': total_files,
                'total_size': total_size,
                'total_size_formatted': self._format_size(total_size),
                'most_common_types': [{'type': ft[0], 'count': ft[1]} for ft in file_types]
            }
        
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")
            return {
                'total_folders': 0,
                'total_files': 0,
                'total_size': 0,
                'total_size_formatted': '0 B',
                'most_common_types': []
            }
        
        finally:
            session.close()
    
    def _format_size(self, size_bytes):
        """
        Formater la taille en octets en format lisible
        
        Args:
            size_bytes (int): Taille en octets
        
        Returns:
            str: Taille formatée (ex: "1.5 MB")
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"
    
    def advanced_search(self, criteria):
        """
        Recherche avancée avec plusieurs critères combinés
        
        Args:
            criteria (dict): Dictionnaire de critères de recherche
                - query (str): Mot-clé général
                - year (int): Année
                - theme (str): Thème
                - sector (str): Secteur
                - file_type (str): Type de fichier
                - min_size (int): Taille minimale en MB
                - max_size (int): Taille maximale en MB
                - start_date (datetime): Date de début
                - end_date (datetime): Date de fin
        
        Returns:
            dict: Résultats de recherche avec folders et files
        """
        results = {
            'folders': [],
            'files': []
        }
        
        # Recherche de dossiers
        results['folders'] = self.search_folders(
            query=criteria.get('query'),
            year=criteria.get('year'),
            theme=criteria.get('theme'),
            sector=criteria.get('sector')
        )
        
        # Recherche de fichiers avec critères supplémentaires
        session = self.db.get_session()
        
        try:
            query_obj = session.query(File).join(Folder).filter(
                Folder.owner_id == self.user.id
            )
            
            # Mot-clé
            if criteria.get('query'):
                query_obj = query_obj.filter(File.name.ilike(f'%{criteria["query"]}%'))
            
            # Type de fichier
            if criteria.get('file_type'):
                query_obj = query_obj.filter(File.file_type.ilike(criteria['file_type']))
            
            # Taille minimale
            if criteria.get('min_size'):
                min_bytes = criteria['min_size'] * 1024 * 1024
                query_obj = query_obj.filter(File.file_size >= min_bytes)
            
            # Taille maximale
            if criteria.get('max_size'):
                max_bytes = criteria['max_size'] * 1024 * 1024
                query_obj = query_obj.filter(File.file_size <= max_bytes)
            
            # Date de début
            if criteria.get('start_date'):
                query_obj = query_obj.filter(File.created_at >= criteria['start_date'])
            
            # Date de fin
            if criteria.get('end_date'):
                query_obj = query_obj.filter(File.created_at <= criteria['end_date'])
            
            results['files'] = query_obj.all()
        
        except Exception as e:
            print(f"Erreur lors de la recherche avancée: {e}")
        
        finally:
            session.close()
        
        return results