

# utils/scanner.py
import os
from pathlib import Path
from typing import List, Dict, Callable, Optional

class FolderScanner:
    """Scanner for folders and files"""
    
    def __init__(self, 
                 extensions_filter: Optional[List[str]] = None,
                 exclude_hidden: bool = True):
        """
        Initialize scanner
        
        Args:
            extensions_filter: List of extensions to include (e.g., ['.pdf', '.docx'])
            exclude_hidden: Exclude hidden files and folders
        """
        self.extensions_filter = extensions_filter
        self.exclude_hidden = exclude_hidden
    
    def scan_folder(self, 
                   folder_path: str, 
                   recursive: bool = True,
                   progress_callback: Optional[Callable] = None) -> Dict:
        """
        Scan folder and return structure
        
        Args:
            folder_path: Path to scan
            recursive: Scan subfolders
            progress_callback: Callback function for progress updates
        
        Returns:
            Dict with folder structure
        """
        result = {
            'path': folder_path,
            'name': os.path.basename(folder_path),
            'files': [],
            'subfolders': [],
            'total_files': 0,
            'total_size': 0
        }
        
        try:
            entries = os.listdir(folder_path)
            
            for entry in entries:
                full_path = os.path.join(folder_path, entry)
                
                # Skip hidden files if configured
                if self.exclude_hidden and entry.startswith('.'):
                    continue
                
                if os.path.isfile(full_path):
                    # Check extension filter
                    if self.extensions_filter:
                        ext = Path(full_path).suffix.lower()
                        if ext not in self.extensions_filter:
                            continue
                    
                    file_info = self._get_file_info(full_path)
                    result['files'].append(file_info)
                    result['total_files'] += 1
                    result['total_size'] += file_info['size']
                    
                    if progress_callback:
                        progress_callback(full_path)
                
                elif os.path.isdir(full_path) and recursive:
                    subfolder = self.scan_folder(full_path, recursive, progress_callback)
                    result['subfolders'].append(subfolder)
                    result['total_files'] += subfolder['total_files']
                    result['total_size'] += subfolder['total_size']
        
        except PermissionError:
            result['error'] = "Permission denied"
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_file_info(self, file_path: str) -> Dict:
        """Get file information"""
        stat = os.stat(file_path)
        
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'extension': Path(file_path).suffix[1:].lower(),
            'modified': stat.st_mtime,
            'created': stat.st_ctime
        }
    
    def get_all_files(self, folder_path: str, recursive: bool = True) -> List[str]:
        """Get list of all file paths in folder"""
        files = []
        
        try:
            for entry in os.listdir(folder_path):
                full_path = os.path.join(folder_path, entry)
                
                if self.exclude_hidden and entry.startswith('.'):
                    continue
                
                if os.path.isfile(full_path):
                    if self.extensions_filter:
                        ext = Path(full_path).suffix.lower()
                        if ext in self.extensions_filter:
                            files.append(full_path)
                    else:
                        files.append(full_path)
                
                elif os.path.isdir(full_path) and recursive:
                    files.extend(self.get_all_files(full_path, recursive))
        
        except (PermissionError, Exception):
            pass
        
        return files
    
    def count_files(self, folder_path: str, recursive: bool = True) -> int:
        """Count total number of files"""
        return len(self.get_all_files(folder_path, recursive))
