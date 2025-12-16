
# utils/validators.py
import re
from pathlib import Path
from typing import Tuple

class Validator:
    """Validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not email:
            return False, "Email est requis"
        
        if not re.match(pattern, email):
            return False, "Format d'email invalide"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username"""
        if not username:
            return False, "Nom d'utilisateur requis"
        
        if len(username) < 3:
            return False, "Nom d'utilisateur trop court (minimum 3 caractères)"
        
        if len(username) > 50:
            return False, "Nom d'utilisateur trop long (maximum 50 caractères)"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Nom d'utilisateur invalide (lettres, chiffres, _ et - uniquement)"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Mot de passe requis"
        
        if len(password) < 6:
            return False, "Mot de passe trop court (minimum 6 caractères)"
        
        if len(password) > 100:
            return False, "Mot de passe trop long"
        
        # Optional: Add more strength requirements
        # has_upper = any(c.isupper() for c in password)
        # has_lower = any(c.islower() for c in password)
        # has_digit = any(c.isdigit() for c in password)
        
        return True, ""
    
    @staticmethod
    def validate_folder_name(name: str) -> Tuple[bool, str]:
        """Validate folder name"""
        if not name:
            return False, "Nom de dossier requis"
        
        if len(name) > 255:
            return False, "Nom de dossier trop long"
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                return False, f"Caractère invalide: {char}"
        
        return True, ""
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """Validate file path"""
        if not file_path:
            return False, "Chemin de fichier requis"
        
        path = Path(file_path)
        
        if not path.exists():
            return False, "Fichier introuvable"
        
        if not path.is_file():
            return False, "Le chemin ne pointe pas vers un fichier"
        
        if not os.access(file_path, os.R_OK):
            return False, "Fichier non accessible en lecture"
        
        return True, ""
    
    @staticmethod
    def validate_year(year: int) -> Tuple[bool, str]:
        """Validate year"""
        if year is None:
            return True, ""
        
        current_year = datetime.now().year
        
        if year < 1900:
            return False, "Année trop ancienne"
        
        if year > current_year + 10:
            return False, "Année trop future"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing invalid characters"""
        # Remove invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename


import os
from datetime import datetime