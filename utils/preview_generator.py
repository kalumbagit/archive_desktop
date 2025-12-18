# =============================================================================
# FICHIER 2: utils/preview_generator.py - COMPLET
# =============================================================================
"""
utils/preview_generator.py
Générateur de prévisualisations pour différents types de fichiers
"""

from pathlib import Path
from typing import Optional, Tuple
import os

# Imports conditionnels pour éviter les erreurs si les bibliothèques ne sont pas installées
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

class PreviewGenerator:
    """Générateur de prévisualisations pour différents types de fichiers"""
    
    # Types de fichiers supportés
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico']
    SUPPORTED_TEXT_FORMATS = ['.txt', '.md', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h']
    SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.docx', '.doc', '.odt', '.rtf']
    
    @staticmethod
    def can_preview(file_path: str) -> bool:
        """
        Vérifier si un fichier peut être prévisualisé
        
        Args:
            file_path (str): Chemin du fichier
        
        Returns:
            bool: True si le fichier peut être prévisualisé
        """
        ext = Path(file_path).suffix.lower()
        return ext in (PreviewGenerator.SUPPORTED_IMAGE_FORMATS + 
                      PreviewGenerator.SUPPORTED_TEXT_FORMATS +
                      PreviewGenerator.SUPPORTED_DOCUMENT_FORMATS)
    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """
        Déterminer le type de fichier pour la prévisualisation
        
        Args:
            file_path (str): Chemin du fichier
        
        Returns:
            str: Type de fichier ('image', 'text', 'pdf', 'document', 'unknown')
        """
        ext = Path(file_path).suffix.lower()
        
        if ext in PreviewGenerator.SUPPORTED_IMAGE_FORMATS:
            return 'image'
        elif ext in PreviewGenerator.SUPPORTED_TEXT_FORMATS:
            return 'text'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in ['.docx', '.doc', '.odt', '.rtf']:
            return 'document'
        else:
            return 'unknown'
    
    @staticmethod
    def generate_image_preview(file_path: str, max_size: Tuple[int, int] = (800, 600)) -> Optional[str]:
        """
        Générer une prévisualisation d'image
        
        Args:
            file_path (str): Chemin de l'image
            max_size (tuple): Taille maximale (largeur, hauteur)
        
        Returns:
            str: Chemin de l'image (original ou redimensionné)
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            img = Image.open(file_path)
            
            # Vérifier si un redimensionnement est nécessaire
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return file_path
        except Exception as e:
            print(f"Erreur lors de la génération de l'aperçu image: {e}")
            return None
    
    @staticmethod
    def extract_text_preview(file_path: str, max_chars: int = 5000) -> Optional[str]:
        """
        Extraire un aperçu texte d'un fichier
        
        Args:
            file_path (str): Chemin du fichier
            max_chars (int): Nombre maximum de caractères à extraire
        
        Returns:
            str: Contenu du fichier (tronqué si nécessaire)
        """
        try:
            # Essayer UTF-8 d'abord
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_chars)
                return content
        except UnicodeDecodeError:
            try:
                # Essayer latin-1 en second
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read(max_chars)
                    return content
            except Exception:
                try:
                    # Essayer cp1252 (Windows)
                    with open(file_path, 'r', encoding='cp1252') as f:
                        content = f.read(max_chars)
                        return content
                except Exception:
                    return None
        except Exception as e:
            print(f"Erreur lors de l'extraction du texte: {e}")
            return None
    
    @staticmethod
    def extract_pdf_preview(file_path: str, max_pages: int = 1) -> Optional[str]:
        """
        Extraire le texte des premières pages d'un PDF
        
        Args:
            file_path (str): Chemin du fichier PDF
            max_pages (int): Nombre maximum de pages à extraire
        
        Returns:
            str: Texte extrait du PDF
        """
        if not PYPDF2_AVAILABLE:
            return "⚠️ PyPDF2 n'est pas installé. Impossible de prévisualiser les PDF.\n\nPour activer cette fonctionnalité, installez PyPDF2:\npip install PyPDF2"
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                if len(pdf_reader.pages) == 0:
                    return "Le PDF est vide (0 pages)."
                
                text = ""
                pages_to_read = min(max_pages, len(pdf_reader.pages))
                
                for i in range(pages_to_read):
                    try:
                        page = pdf_reader.pages[i]
                        page_text = page.extract_text()
                        
                        if page_text:
                            text += f"--- Page {i+1} ---\n\n{page_text}\n\n"
                        else:
                            text += f"--- Page {i+1} ---\n\n[Aucun texte extractible]\n\n"
                    except Exception as e:
                        text += f"--- Page {i+1} ---\n\n[Erreur lors de l'extraction: {str(e)}]\n\n"
                
                if not text.strip():
                    return "Le PDF ne contient pas de texte extractible.\nIl peut s'agir d'un PDF contenant uniquement des images."
                
                return text
        
        except Exception as e:
            return f"❌ Erreur lors de la lecture du PDF:\n{str(e)}\n\nLe fichier pourrait être:\n- Protégé par mot de passe\n- Corrompu\n- Dans un format non standard"
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Obtenir des informations détaillées sur un fichier
        
        Args:
            file_path (str): Chemin du fichier
        
        Returns:
            dict: Informations sur le fichier
        """
        try:
            stat = os.stat(file_path)
            
            return {
                'name': Path(file_path).name,
                'size': stat.st_size,
                'size_formatted': PreviewGenerator._format_size(stat.st_size),
                'extension': Path(file_path).suffix[1:].upper() if Path(file_path).suffix else 'Aucune',
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'path': file_path,
                'exists': True
            }
        except Exception as e:
            return {
                'name': Path(file_path).name,
                'size': 0,
                'size_formatted': '0 B',
                'extension': 'Inconnu',
                'modified': 0,
                'created': 0,
                'path': file_path,
                'exists': False,
                'error': str(e)
            }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        Formater la taille d'un fichier en format lisible
        
        Args:
            size_bytes (int): Taille en octets
        
        Returns:
            str: Taille formatée (ex: "1.5 MB")
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"
