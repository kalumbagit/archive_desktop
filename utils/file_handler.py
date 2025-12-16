
# utils/file_handler.py
import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Tuple

class FileHandler:
    """Handle file operations"""
    
    @staticmethod
    def copy_file(source: str, destination: str) -> Tuple[bool, str]:
        """
        Copy file from source to destination
        
        Returns:
            Tuple[bool, str]: (Success, Error message or destination path)
        """
        try:
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True, str(dest_path)
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def move_file(source: str, destination: str) -> Tuple[bool, str]:
        """Move file from source to destination"""
        try:
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(source, destination)
            return True, str(dest_path)
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def delete_file(file_path: str) -> Tuple[bool, str]:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, "Fichier supprimé"
            return False, "Fichier introuvable"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except:
            return None
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm='sha256') -> Optional[str]:
        """Calculate file hash"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except:
            return None
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes is None or size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get file extension without dot"""
        return Path(file_path).suffix[1:].lower()
    
    @staticmethod
    def is_valid_file(file_path: str) -> bool:
        """Check if file exists and is accessible"""
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
