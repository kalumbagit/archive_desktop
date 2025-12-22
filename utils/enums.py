import enum
class UserRole(enum.Enum):
    """Rôles des utilisateurs"""
    USER = "user"           # Utilisateur normal
    ADMIN = "admin"         # Administrateur
    SUPERUSER = "superuser" # Super utilisateur (accès total)


class FolderVisibility(enum.Enum):
    """Visibilité des dossiers"""
    PRIVATE = "private"   # Visible uniquement par le propriétaire
    SHARED = "shared"     # Partagé avec certains utilisateurs
    PUBLIC = "public"     # Accessible à tous les utilisateurs


class SharePermission(enum.Enum):
    """Permissions de partage"""
    READ = "read"           # Lecture seule
    WRITE = "write"         # Lecture et écriture (ajouter des fichiers)
    MANAGE = "manage"       # Gestion complète (renommer, supprimer)


