#!/usr/bin/env python3
"""
Format Converter for Multi-Modal Annotations

This module provides functions to convert between different annotation formats
commonly used in computer vision and NLP tasks.

Supported conversions:
- COCO JSON ↔ YOLO TXT
- XML ↔ JSON
- CSV ↔ JSON
- CoNLL ↔ JSON

Author: MultiModal AI Dataset Creator
"""

import json
import csv
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd


class FormatConverter:
    """Main class for handling format conversions between annotation formats."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        
    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[FormatConverter] {message}")

    # COCO ↔ YOLO Conversions
    def coco_to_yolo(self, coco_json_path: str, output_dir: str, 
                     image_width: int = None, image_height: int = None) -> bool:
        """
        Convert COCO JSON format to YOLO TXT format.
        
        Args:
            coco_json_path: Path to COCO JSON file
            output_dir: Directory to save YOLO TXT files
            image_width: Default image width (if not in COCO JSON)
            image_height: Default image height (if not in COCO JSON)
            
        Returns:
            bool: True if conversion successful
        """
        try:
            with open(coco_json_path, 'r') as f:
                coco_data = json.load(f)
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Create category mapping
            categories = {cat['id']: cat['name'] for cat in coco_data.get('categories', [])}
            category_to_id = {name: idx for idx, name in enumerate(categories.values())}
            
            # Group annotations by image
            image_annotations = {}
            for ann in coco_data.get('annotations', []):
                image_id = ann['image_id']
                if image_id not in image_annotations:
                    image_annotations[image_id] = []
                image_annotations[image_id].append(ann)
            
            # Convert each image's annotations
            for image in coco_data.get('images', []):
                image_id = image['id']
                filename = Path(image['file_name']).stem
                
                img_width = image.get('width', image_width)
                img_height = image.get('height', image_height)
                
                if not img_width or not img_height:
                    self.log(f"Warning: Missing dimensions for {filename}")
                    continue
                
                yolo_lines = []
                if image_id in image_annotations:
                    for ann in image_annotations[image_id]:
                        bbox = ann['bbox']  # [x, y, width, height]
                        category_name = categories.get(ann['category_id'], 'unknown')
                        class_id = category_to_id.get(category_name, 0)
                        
                        # Convert to YOLO format (normalized center coordinates)
                        x_center = (bbox[0] + bbox[2] / 2) / img_width
                        y_center = (bbox[1] + bbox[3] / 2) / img_height
                        norm_width = bbox[2] / img_width
                        norm_height = bbox[3] / img_height
                        
                        yolo_lines.append(f"{class_id} {x_center} {y_center} {norm_width} {norm_height}")
                
                # Save YOLO format file
                output_path = os.path.join(output_dir, f"{filename}.txt")
                with open(output_path, 'w') as f:
                    f.write('\n'.join(yolo_lines))
            
            # Save classes file
            with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
                for class_name in category_to_id.keys():
                    f.write(f"{class_name}\n")
            
            self.log(f"Successfully converted COCO to YOLO format in {output_dir}")
            return True
            
        except Exception as e:
            self.log(f"Error converting COCO to YOLO: {str(e)}")
            return False

    def yolo_to_coco(self, yolo_dir: str, images_dir: str, output_path: str,
                     classes_file: str = None) -> bool:
        """
        Convert YOLO TXT format to COCO JSON format.
        
        Args:
            yolo_dir: Directory containing YOLO TXT files
            images_dir: Directory containing corresponding images
            output_path: Path to save COCO JSON file
            classes_file: Path to classes.txt file
            
        Returns:
            bool: True if conversion successful
        """
        try:
            # Load classes
            if classes_file and os.path.exists(classes_file):
                with open(classes_file, 'r') as f:
                    classes = [line.strip() for line in f.readlines()]
            else:
                classes_path = os.path.join(yolo_dir, 'classes.txt')
                if os.path.exists(classes_path):
                    with open(classes_path, 'r') as f:
                        classes = [line.strip() for line in f.readlines()]
                else:
                    self.log("Warning: No classes file found, using generic class names")
                    classes = ['class_0', 'class_1', 'class_2']  # Generic fallback
            
            coco_data = {
                "info": {
                    "description": "Dataset converted from YOLO format",
                    "version": "1.0",
                    "year": 2024,
                    "contributor": "MultiModal AI Dataset Creator"
                },
                "licenses": [],
                "images": [],
                "annotations": [],
                "categories": []
            }
            
            # Add categories
            for idx, class_name in enumerate(classes):
                coco_data["categories"].append({
                    "id": idx,
                    "name": class_name,
                    "supercategory": "object"
                })
            
            annotation_id = 1
            
            # Process each YOLO file
            for txt_file in Path(yolo_dir).glob("*.txt"):
                if txt_file.name == "classes.txt":
                    continue
                
                image_name = txt_file.stem
                
                # Find corresponding image
                image_path = None
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    potential_path = os.path.join(images_dir, f"{image_name}{ext}")
                    if os.path.exists(potential_path):
                        image_path = potential_path
                        break
                
                if not image_path:
                    self.log(f"Warning: No image found for {txt_file.name}")
                    continue
                
                # Get image dimensions (you might need PIL for this)
                try:
                    from PIL import Image
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                except ImportError:
                    self.log("PIL not available, using default dimensions")
                    img_width, img_height = 640, 480
                
                image_id = len(coco_data["images"])
                coco_data["images"].append({
                    "id": image_id,
                    "width": img_width,
                    "height": img_height,
                    "file_name": os.path.basename(image_path)
                })
                
                # Read YOLO annotations
                with open(txt_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                class_id = int(parts[0])
                                x_center = float(parts[1]) * img_width
                                y_center = float(parts[2]) * img_height
                                width = float(parts[3]) * img_width
                                height = float(parts[4]) * img_height
                                
                                # Convert to COCO bbox format [x, y, width, height]
                                bbox = [
                                    x_center - width / 2,
                                    y_center - height / 2,
                                    width,
                                    height
                                ]
                                
                                coco_data["annotations"].append({
                                    "id": annotation_id,
                                    "image_id": image_id,
                                    "category_id": class_id,
                                    "bbox": bbox,
                                    "area": width * height,
                                    "iscrowd": 0
                                })
                                annotation_id += 1
            
            # Save COCO JSON
            with open(output_path, 'w') as f:
                json.dump(coco_data, f, indent=2)
            
            self.log(f"Successfully converted YOLO to COCO format: {output_path}")
            return True
            
        except Exception as e:
            self.log(f"Error converting YOLO to COCO: {str(e)}")
            return False

    # Text annotation conversions
    def csv_to_json(self, csv_path: str, output_path: str, 
                    text_column: str = 'text', label_column: str = 'label') -> bool:
        """Convert CSV annotations to JSON format."""
        try:
            df = pd.read_csv(csv_path)
            
            data = []
            for _, row in df.iterrows():
                data.append({
                    'text': row[text_column],
                    'label': row[label_column],
                    'metadata': {k: v for k, v in row.items() 
                                if k not in [text_column, label_column]}
                })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.log(f"Successfully converted CSV to JSON: {output_path}")
            return True
            
        except Exception as e:
            self.log(f"Error converting CSV to JSON: {str(e)}")
            return False

    def json_to_csv(self, json_path: str, output_path: str) -> bool:
        """Convert JSON annotations to CSV format."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Flatten the data structure
            rows = []
            for item in data:
                row = {
                    'text': item.get('text', ''),
                    'label': item.get('label', '')
                }
                # Add metadata fields
                if 'metadata' in item:
                    row.update(item['metadata'])
                rows.append(row)
            
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False)
            
            self.log(f"Successfully converted JSON to CSV: {output_path}")
            return True
            
        except Exception as e:
            self.log(f"Error converting JSON to CSV: {str(e)}")
            return False


def main():
    """Example usage of the FormatConverter class."""
    converter = FormatConverter(verbose=True)
    
    # Example conversions (uncomment to test)
    # converter.coco_to_yolo('annotations/coco_annotations.json', 'output/yolo/')
    # converter.yolo_to_coco('annotations/yolo/', 'data/images/', 'output/coco.json')
    # converter.csv_to_json('annotations/text_data.csv', 'output/text_data.json')
    # converter.json_to_csv('annotations/text_data.json', 'output/text_data.csv')
    
    print("Format converter initialized. Import this module to use conversion functions.")


if __name__ == "__main__":
    main()
