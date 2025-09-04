#!/usr/bin/env python3
"""
File Renamer for Multi-Modal Dataset Organization

This module provides systematic file renaming functionality for organizing
multi-modal datasets with consistent naming conventions.

Features:
- Systematic renaming with prefixes and sequential numbering
- Batch renaming operations
- Safe renaming with backup options
- Metadata preservation
- Format validation

Author: MultiModal AI Dataset Creator
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from collections import defaultdict


class DatasetFileRenamer:
    """Main class for systematic file renaming in multi-modal datasets."""
    
    def __init__(self, verbose: bool = True, create_backup: bool = True):
        self.verbose = verbose
        self.create_backup = create_backup
        self.rename_log = []
        
    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[FileRenamer] {message}")

    def create_backup_if_needed(self, file_path: str) -> bool:
        """Create a backup of the file if backup is enabled."""
        if not self.create_backup:
            return True
            
        try:
            backup_dir = os.path.join(os.path.dirname(file_path), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            return True
            
        except Exception as e:
            self.log(f"Failed to create backup for {file_path}: {str(e)}")
            return False

    def rename_images_systematic(self, images_dir: str, prefix: str = "img", 
                                start_index: int = 1, zero_padding: int = 4) -> Dict[str, str]:
        """
        Rename image files systematically.
        
        Args:
            images_dir: Directory containing image files
            prefix: Prefix for renamed files
            start_index: Starting index for numbering
            zero_padding: Number of digits for zero padding
            
        Returns:
            Dict mapping old filenames to new filenames
        """
        rename_mapping = {}
        
        try:
            # Supported image extensions
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
            
            # Get all image files
            image_files = []
            for file_path in Path(images_dir).iterdir():
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    image_files.append(file_path)
            
            # Sort for consistent ordering
            image_files.sort()
            
            self.log(f"Found {len(image_files)} image files to rename")
            
            # Rename each file
            current_index = start_index
            for file_path in image_files:
                old_name = file_path.name
                extension = file_path.suffix.lower()
                
                # Create new name
                new_name = f"{prefix}_{current_index:0{zero_padding}d}{extension}"
                new_path = file_path.parent / new_name
                
                # Check if new name already exists
                if new_path.exists() and new_path != file_path:
                    self.log(f"Warning: {new_name} already exists, skipping {old_name}")
                    continue
                
                # Create backup if needed
                if not self.create_backup_if_needed(str(file_path)):
                    continue
                
                # Rename the file
                try:
                    file_path.rename(new_path)
                    rename_mapping[old_name] = new_name
                    self.rename_log.append({
                        'old_name': old_name,
                        'new_name': new_name,
                        'type': 'image',
                        'directory': str(images_dir)
                    })
                    current_index += 1
                    
                except Exception as e:
                    self.log(f"Failed to rename {old_name}: {str(e)}")
            
            self.log(f"Successfully renamed {len(rename_mapping)} image files")
            
        except Exception as e:
            self.log(f"Error in systematic image renaming: {str(e)}")
        
        return rename_mapping

    def rename_audio_systematic(self, audio_dir: str, prefix: str = "audio", 
                               start_index: int = 1, zero_padding: int = 4) -> Dict[str, str]:
        """
        Rename audio files systematically.
        
        Args:
            audio_dir: Directory containing audio files
            prefix: Prefix for renamed files
            start_index: Starting index for numbering
            zero_padding: Number of digits for zero padding
            
        Returns:
            Dict mapping old filenames to new filenames
        """
        rename_mapping = {}
        
        try:
            # Supported audio extensions
            audio_extensions = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a'}
            
            # Get all audio files
            audio_files = []
            for file_path in Path(audio_dir).iterdir():
                if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                    audio_files.append(file_path)
            
            # Sort for consistent ordering
            audio_files.sort()
            
            self.log(f"Found {len(audio_files)} audio files to rename")
            
            # Rename each file
            current_index = start_index
            for file_path in audio_files:
                old_name = file_path.name
                extension = file_path.suffix.lower()
                
                # Create new name
                new_name = f"{prefix}_{current_index:0{zero_padding}d}{extension}"
                new_path = file_path.parent / new_name
                
                # Check if new name already exists
                if new_path.exists() and new_path != file_path:
                    self.log(f"Warning: {new_name} already exists, skipping {old_name}")
                    continue
                
                # Create backup if needed
                if not self.create_backup_if_needed(str(file_path)):
                    continue
                
                # Rename the file
                try:
                    file_path.rename(new_path)
                    rename_mapping[old_name] = new_name
                    self.rename_log.append({
                        'old_name': old_name,
                        'new_name': new_name,
                        'type': 'audio',
                        'directory': str(audio_dir)
                    })
                    current_index += 1
                    
                except Exception as e:
                    self.log(f"Failed to rename {old_name}: {str(e)}")
            
            self.log(f"Successfully renamed {len(rename_mapping)} audio files")
            
        except Exception as e:
            self.log(f"Error in systematic audio renaming: {str(e)}")
        
        return rename_mapping

    def rename_by_category(self, files_dir: str, category_mapping: Dict[str, str],
                          prefix_format: str = "{category}_{index:04d}") -> Dict[str, str]:
        """
        Rename files based on categories.
        
        Args:
            files_dir: Directory containing files
            category_mapping: Dict mapping filename to category
            prefix_format: Format string for new names (supports {category} and {index})
            
        Returns:
            Dict mapping old filenames to new filenames
        """
        rename_mapping = {}
        category_counters = defaultdict(int)
        
        try:
            for old_filename, category in category_mapping.items():
                old_path = Path(files_dir) / old_filename
                
                if not old_path.exists():
                    self.log(f"Warning: File {old_filename} not found")
                    continue
                
                # Increment counter for this category
                category_counters[category] += 1
                index = category_counters[category]
                
                # Create new filename
                extension = old_path.suffix
                new_name = prefix_format.format(category=category, index=index) + extension
                new_path = old_path.parent / new_name
                
                # Check if new name already exists
                if new_path.exists() and new_path != old_path:
                    self.log(f"Warning: {new_name} already exists, skipping {old_filename}")
                    continue
                
                # Create backup if needed
                if not self.create_backup_if_needed(str(old_path)):
                    continue
                
                # Rename the file
                try:
                    old_path.rename(new_path)
                    rename_mapping[old_filename] = new_name
                    self.rename_log.append({
                        'old_name': old_filename,
                        'new_name': new_name,
                        'category': category,
                        'type': 'category_based',
                        'directory': str(files_dir)
                    })
                    
                except Exception as e:
                    self.log(f"Failed to rename {old_filename}: {str(e)}")
            
            self.log(f"Successfully renamed {len(rename_mapping)} files by category")
            
        except Exception as e:
            self.log(f"Error in category-based renaming: {str(e)}")
        
        return rename_mapping

    def update_annotation_references(self, annotation_file: str, rename_mapping: Dict[str, str],
                                   backup_annotations: bool = True) -> bool:
        """
        Update filename references in annotation files.
        
        Args:
            annotation_file: Path to annotation file (JSON or CSV)
            rename_mapping: Dict mapping old filenames to new filenames
            backup_annotations: Whether to backup annotation file
            
        Returns:
            bool: True if update successful
        """
        try:
            if backup_annotations:
                self.create_backup_if_needed(annotation_file)
            
            if annotation_file.endswith('.json'):
                return self._update_json_annotations(annotation_file, rename_mapping)
            elif annotation_file.endswith('.csv'):
                return self._update_csv_annotations(annotation_file, rename_mapping)
            else:
                self.log(f"Unsupported annotation format: {annotation_file}")
                return False
                
        except Exception as e:
            self.log(f"Failed to update annotation references: {str(e)}")
            return False

    def _update_json_annotations(self, json_file: str, rename_mapping: Dict[str, str]) -> bool:
        """Update filename references in JSON annotation file."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            updates_made = 0
            
            # Handle COCO format
            if 'images' in data:
                for image_info in data['images']:
                    old_filename = image_info.get('file_name', '')
                    if old_filename in rename_mapping:
                        image_info['file_name'] = rename_mapping[old_filename]
                        updates_made += 1
            
            # Handle other JSON formats
            elif isinstance(data, list):
                for item in data:
                    for key in ['filename', 'file_name', 'image_file', 'audio_file']:
                        if key in item and item[key] in rename_mapping:
                            item[key] = rename_mapping[item[key]]
                            updates_made += 1
            
            # Save updated JSON
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.log(f"Updated {updates_made} filename references in {json_file}")
            return True
            
        except Exception as e:
            self.log(f"Failed to update JSON annotations: {str(e)}")
            return False

    def _update_csv_annotations(self, csv_file: str, rename_mapping: Dict[str, str]) -> bool:
        """Update filename references in CSV annotation file."""
        try:
            import pandas as pd
            
            df = pd.read_csv(csv_file)
            updates_made = 0
            
            # Common filename columns
            filename_columns = ['filename', 'file_name', 'image_file', 'audio_file']
            
            for col in filename_columns:
                if col in df.columns:
                    for idx, old_filename in enumerate(df[col]):
                        if old_filename in rename_mapping:
                            df.at[idx, col] = rename_mapping[old_filename]
                            updates_made += 1
            
            # Save updated CSV
            df.to_csv(csv_file, index=False)
            
            self.log(f"Updated {updates_made} filename references in {csv_file}")
            return True
            
        except Exception as e:
            self.log(f"Failed to update CSV annotations: {str(e)}")
            return False

    def save_rename_log(self, log_file: str) -> bool:
        """Save the rename operations log to a file."""
        try:
            with open(log_file, 'w') as f:
                json.dump(self.rename_log, f, indent=2)
            
            self.log(f"Rename log saved to {log_file}")
            return True
            
        except Exception as e:
            self.log(f"Failed to save rename log: {str(e)}")
            return False

    def undo_last_rename_batch(self) -> bool:
        """Undo the last batch of rename operations using the log."""
        if not self.rename_log:
            self.log("No rename operations to undo")
            return False
        
        try:
            # Group by directory for batch operations
            last_batch = self.rename_log[-1:]  # Get last operation
            
            for operation in reversed(last_batch):
                old_name = operation['old_name']
                new_name = operation['new_name']
                directory = operation['directory']
                
                old_path = Path(directory) / old_name
                new_path = Path(directory) / new_name
                
                if new_path.exists():
                    new_path.rename(old_path)
                    self.log(f"Reverted: {new_name} -> {old_name}")
            
            # Remove undone operations from log
            self.rename_log = self.rename_log[:-1]
            return True
            
        except Exception as e:
            self.log(f"Failed to undo rename operations: {str(e)}")
            return False


def main():
    """Example usage of the DatasetFileRenamer class."""
    renamer = DatasetFileRenamer(verbose=True, create_backup=True)
    
    # Example usage (uncomment to test)
    # image_mapping = renamer.rename_images_systematic('data/images/', 'img', 1, 4)
    # audio_mapping = renamer.rename_audio_systematic('data/audio/', 'audio', 1, 4)
    # renamer.update_annotation_references('annotations/image_labels.json', image_mapping)
    # renamer.save_rename_log('qa/rename_log.json')
    
    print("File Renamer initialized. Import this module to use renaming functions.")


if __name__ == "__main__":
    main()
