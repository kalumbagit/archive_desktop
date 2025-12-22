# controllers/sharing_controller.py
from database.db_manager import DatabaseManager
from models.folder import Folder, FolderVisibility
from models.folder_share import FolderShare, SharePermission
from models.user import User
from controllers.audit_controller import AuditController
from sqlalchemy.orm import selectinload

class SharingController:
    def __init__(self, user, db: DatabaseManager):
        self.user = user
        self.db = db
        self.audit = AuditController(user, db)
    
    # ------------------------------
    # Méthodes utilitaires
    # ------------------------------
    def _load_all_subfolders(self, folder, session):
        """Forcer le chargement récursif de tous les sous-dossiers"""
        for sub in folder.subfolders:
            self._load_all_subfolders(sub, session)

    def share_folder(self, folder_id, user_id, permission=SharePermission.READ):
        """Partager un dossier avec un utilisateur"""
        session = self.db.get_session()
        try:
            # Vérifier que le dossier existe et appartient à l'utilisateur
            folder = session.query(Folder).filter(Folder.id == folder_id).first()
            if not folder:
                return False, "Dossier non trouvé"
            
            if folder.owner_id != self.user.id and not self.user.is_superuser():
                return False, "Vous n'avez pas la permission de partager ce dossier"
            
            # Vérifier que l'utilisateur cible existe
            target_user = session.query(User).filter(User.id == user_id).first()
            if not target_user:
                return False, "Utilisateur non trouvé"
            
            # Vérifier si déjà partagé
            existing_share = session.query(FolderShare).filter(
                FolderShare.folder_id == folder_id,
                FolderShare.user_id == user_id
            ).first()
            
            if existing_share:
                # Mettre à jour la permission
                existing_share.permission = permission
                session.commit()
                
                self.audit.log_action('UPDATE', 'SHARE', existing_share.id,
                                    f"Permission mise à jour pour {target_user.username}")
                return True, "Permission mise à jour"
            
            # Créer le partage
            share = FolderShare(
                folder_id=folder_id,
                user_id=user_id,
                permission=permission,
                shared_by=self.user.id
            )
            
            session.add(share)
            
            # Mettre à jour la visibilité du dossier
            if folder.visibility == FolderVisibility.PRIVATE:
                folder.visibility = FolderVisibility.SHARED
            
            session.commit()
            
            self.audit.log_action('CREATE', 'SHARE', share.id,
                                f"Dossier '{folder.name}' partagé avec {target_user.username}")
            
            return True, f"Dossier partagé avec {target_user.username}"
            
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def unshare_folder(self, folder_id, user_id):
        """Retirer le partage d'un dossier"""
        session = self.db.get_session()
        try:
            folder = session.query(Folder).filter(Folder.id == folder_id).first()
            if not folder:
                return False, "Dossier non trouvé"
            
            if folder.owner_id != self.user.id and not self.user.is_superuser():
                return False, "Permission refusée"
            
            share = session.query(FolderShare).filter(
                FolderShare.folder_id == folder_id,
                FolderShare.user_id == user_id
            ).first()
            
            if not share:
                return False, "Partage non trouvé"
            
            target_user = share.user
            session.delete(share)
            
            # Si plus de partages, remettre en privé
            remaining_shares = session.query(FolderShare).filter(
                FolderShare.folder_id == folder_id
            ).count()
            
            if remaining_shares == 0 and folder.visibility == FolderVisibility.SHARED:
                folder.visibility = FolderVisibility.PRIVATE
            
            session.commit()
            
            self.audit.log_action('DELETE', 'SHARE', folder_id,
                                f"Partage retiré pour {target_user.username}")
            
            return True, "Partage retiré"
            
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def set_folder_public(self, folder_id, is_public=True):
        """Rendre un dossier public ou privé"""
        session = self.db.get_session()
        try:
            folder = session.query(Folder).filter(Folder.id == folder_id).first()
            if not folder:
                return False, "Dossier non trouvé"
            
            if folder.owner_id != self.user.id and not self.user.is_superuser():
                return False, "Permission refusée"
            
            if is_public:
                folder.visibility = FolderVisibility.PUBLIC
                message = "Dossier rendu public"
            else:
                # Vérifier s'il y a des partages
                has_shares = session.query(FolderShare).filter(
                    FolderShare.folder_id == folder_id
                ).count() > 0
                
                folder.visibility = FolderVisibility.SHARED if has_shares else FolderVisibility.PRIVATE
                message = "Dossier rendu privé"
            
            session.commit()
            
            self.audit.log_action('UPDATE', 'FOLDER', folder_id,
                                f"Visibilité changée: {folder.visibility.value}")
            
            return True, message
            
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def get_public_folders(self):
        """Récupérer tous les dossiers publics"""
        session = self.db.get_session()
        try:
            folders = (
                session.query(Folder)
                .options(
                    selectinload(Folder.owner),
                    selectinload(Folder.subfolders),
                    selectinload(Folder.files)
                )
                .filter(Folder.visibility == FolderVisibility.PUBLIC)
                .all()
            )
            
            for folder in folders:
                self._load_all_subfolders(folder, session)
            session.expunge_all()
            return folders
            
        finally:
            session.close()
    
    def get_shared_with_me(self):
        """Récupérer les dossiers partagés avec moi"""
        session = self.db.get_session()
        try:
            shares = (
                session.query(FolderShare)
                .options(selectinload(FolderShare.folder))
                .filter(FolderShare.user_id == self.user.id)
                .all()
            )
            
            folders = [share.folder for share in shares]
            for folder in folders:
                self._load_all_subfolders(folder, session)
            session.expunge_all()
            
            return folders
            
        finally:
            session.close()
    
    def get_folder_shares(self, folder_id):
        """Récupérer la liste des partages d'un dossier"""
        session = self.db.get_session()
        try:
            folder = session.query(Folder).filter(Folder.id == folder_id).first()
            if not folder:
                return None
            
            if folder.owner_id != self.user.id and not self.user.is_superuser():
                return None
            
            shares = (
                session.query(FolderShare)
                .options(selectinload(FolderShare.user))
                .filter(FolderShare.folder_id == folder_id)
                .all()
            )

            # Charger récursivement les sous-dossiers du dossier partagé
            self._load_all_subfolders(folder, session)
            session.expunge_all()
            return shares
            
        finally:
            session.close()
    
    def get_all_accessible_folders(self):
        """
        Récupérer tous les dossiers accessibles par l'utilisateur:
        - Ses propres dossiers
        - Les dossiers publics
        - Les dossiers partagés avec lui
        - Si superuser: TOUS les dossiers
        """
        session = self.db.get_session()
        try:
            if self.user.is_superuser():
                # Superuser voit tout
                folders = (
                    session.query(Folder)
                    .options(selectinload(Folder.subfolders))
                    .filter(Folder.parent_id.is_(None))
                    .all()
                )
            else:
                # Dossiers personnels
                my_folders = (
                    session.query(Folder)
                    .options(selectinload(Folder.subfolders))
                    .filter(
                        Folder.owner_id == self.user.id,
                        Folder.parent_id.is_(None)
                    )
                    .all()
                )
                
                # Dossiers publics des autres
                public_folders = (
                    session.query(Folder)
                    .options(selectinload(Folder.subfolders))
                    .filter(
                        Folder.visibility == FolderVisibility.PUBLIC,
                        Folder.owner_id != self.user.id,
                        Folder.parent_id.is_(None)
                    )
                    .all()
                )
                
                # Dossiers partagés avec moi
                shared_folder_ids = [
                    share.folder_id for share in 
                    session.query(FolderShare.folder_id)
                    .filter(FolderShare.user_id == self.user.id)
                    .all()
                ]
                
                shared_folders = (
                    session.query(Folder)
                    .options(selectinload(Folder.subfolders))
                    .filter(
                        Folder.id.in_(shared_folder_ids),
                        Folder.parent_id.is_(None)
                    )
                    .all()
                ) if shared_folder_ids else []
                
                folders = my_folders + public_folders + shared_folders
            for folder in folders:
                self._load_all_subfolders(folder, session)
            session.expunge_all()
            return folders
            
        finally:
            session.close()
