import tarfile
import os
import tempfile
import shutil

class UAFUpdater:
    """Updates or adds files to an existing UAF archive."""
    
    def __init__(self, uaf_path: str):
        self.uaf_path = uaf_path
        
    def update(self, file_path: str, archive_name: str = None):
        """
        Add or update a file in the UAF archive.
        
        Args:
            file_path: Path to the file to add/update.
            archive_name: Name to use inside archive. Defaults to filename.
        """
        if not os.path.exists(self.uaf_path):
            raise FileNotFoundError(f"UAF file not found: {self.uaf_path}")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Determine the name inside the archive
        if archive_name is None:
            archive_name = os.path.basename(file_path)
        
        print(f"Updating '{archive_name}' in {self.uaf_path}...")
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="uaf_update_")
        
        try:
            # Extract existing archive
            with tarfile.open(self.uaf_path, "r:gz") as tar:
                tar.extractall(path=temp_dir)
            
            # Copy the new/updated file
            dest_path = os.path.join(temp_dir, archive_name)
            
            # Create parent directories if needed
            dest_parent = os.path.dirname(dest_path)
            if dest_parent and not os.path.exists(dest_parent):
                os.makedirs(dest_parent)
            
            shutil.copy2(file_path, dest_path)
            print(f"  [OK] Added/Updated: {archive_name}")
            
            # Repack the archive
            with tarfile.open(self.uaf_path, "w:gz") as tar:
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    tar.add(item_path, arcname=item)
            
            print(f"Successfully updated {self.uaf_path}")
            
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
