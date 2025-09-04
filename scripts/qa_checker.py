#!/usr/bin/env python3
"""
Quality Assurance Checker for Multi-Modal Annotations

This module provides comprehensive QA functionality for validating annotations
across different modalities (image, text, audio).

Features:
- Annotation consistency validation
- Missing label detection
- Format compliance checking
- Statistical analysis and reporting
- Automated QA report generation

Author: MultiModal AI Dataset Creator
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from collections import Counter, defaultdict
import datetime


class AnnotationQAChecker:
    """Main class for quality assurance of multi-modal annotations."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.qa_results = {}
        
    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[QAChecker] {message}")

    def validate_image_annotations(self, annotations_path: str, images_dir: str) -> Dict[str, Any]:
        """
        Validate image annotations (COCO format).
        
        Args:
            annotations_path: Path to COCO JSON annotations
            images_dir: Directory containing images
            
        Returns:
            Dict containing validation results
        """
        results = {
            'total_images': 0,
            'total_annotations': 0,
            'missing_images': [],
            'invalid_bboxes': [],
            'class_distribution': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load annotations
            with open(annotations_path, 'r') as f:
                coco_data = json.load(f)
            
            # Validate basic structure
            required_keys = ['images', 'annotations', 'categories']
            for key in required_keys:
                if key not in coco_data:
                    results['errors'].append(f"Missing required key: {key}")
                    return results
            
            results['total_images'] = len(coco_data['images'])
            results['total_annotations'] = len(coco_data['annotations'])
            
            # Create mappings
            image_id_to_file = {img['id']: img['file_name'] for img in coco_data['images']}
            category_id_to_name = {cat['id']: cat['name'] for cat in coco_data['categories']}
            
            # Check image files exist
            for image_info in coco_data['images']:
                image_path = os.path.join(images_dir, image_info['file_name'])
                if not os.path.exists(image_path):
                    results['missing_images'].append(image_info['file_name'])
            
            # Validate annotations
            class_counts = Counter()
            for ann in coco_data['annotations']:
                # Check required fields
                required_fields = ['id', 'image_id', 'category_id', 'bbox']
                for field in required_fields:
                    if field not in ann:
                        results['errors'].append(f"Annotation {ann.get('id', 'unknown')} missing {field}")
                        continue
                
                # Validate bbox
                bbox = ann['bbox']
                if len(bbox) != 4:
                    results['invalid_bboxes'].append(f"Annotation {ann['id']}: bbox must have 4 values")
                elif any(val < 0 for val in bbox):
                    results['invalid_bboxes'].append(f"Annotation {ann['id']}: negative bbox values")
                elif bbox[2] <= 0 or bbox[3] <= 0:
                    results['invalid_bboxes'].append(f"Annotation {ann['id']}: zero or negative width/height")
                
                # Count classes
                category_name = category_id_to_name.get(ann['category_id'], 'unknown')
                class_counts[category_name] += 1
            
            results['class_distribution'] = dict(class_counts)
            
            # Check for class imbalance
            if class_counts:
                max_count = max(class_counts.values())
                min_count = min(class_counts.values())
                if max_count > min_count * 10:  # 10x imbalance threshold
                    results['warnings'].append(f"Significant class imbalance detected: {max_count}:{min_count}")
            
        except Exception as e:
            results['errors'].append(f"Failed to validate image annotations: {str(e)}")
        
        return results

    def validate_text_annotations(self, annotations_path: str) -> Dict[str, Any]:
        """
        Validate text annotations (CSV or JSON format).
        
        Args:
            annotations_path: Path to text annotations file
            
        Returns:
            Dict containing validation results
        """
        results = {
            'total_samples': 0,
            'missing_text': 0,
            'missing_labels': 0,
            'empty_text': 0,
            'label_distribution': {},
            'text_length_stats': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load annotations based on file extension
            if annotations_path.endswith('.csv'):
                df = pd.read_csv(annotations_path)
                data = df.to_dict('records')
            elif annotations_path.endswith('.json'):
                with open(annotations_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                results['errors'].append("Unsupported file format. Use CSV or JSON.")
                return results
            
            results['total_samples'] = len(data)
            
            # Validate each sample
            text_lengths = []
            label_counts = Counter()
            
            for i, item in enumerate(data):
                # Check for required fields
                text = item.get('text', '')
                label = item.get('label', '')
                
                if not text:
                    results['missing_text'] += 1
                elif isinstance(text, str) and len(text.strip()) == 0:
                    results['empty_text'] += 1
                else:
                    text_lengths.append(len(str(text)))
                
                if not label:
                    results['missing_labels'] += 1
                else:
                    label_counts[str(label)] += 1
            
            results['label_distribution'] = dict(label_counts)
            
            # Text length statistics
            if text_lengths:
                results['text_length_stats'] = {
                    'min': min(text_lengths),
                    'max': max(text_lengths),
                    'mean': sum(text_lengths) / len(text_lengths),
                    'median': sorted(text_lengths)[len(text_lengths) // 2]
                }
            
            # Check for potential issues
            if results['missing_text'] > results['total_samples'] * 0.1:
                results['warnings'].append(f"High percentage of missing text: {results['missing_text']}/{results['total_samples']}")
            
            if results['missing_labels'] > results['total_samples'] * 0.05:
                results['warnings'].append(f"High percentage of missing labels: {results['missing_labels']}/{results['total_samples']}")
            
        except Exception as e:
            results['errors'].append(f"Failed to validate text annotations: {str(e)}")
        
        return results

    def validate_audio_annotations(self, annotations_path: str, audio_dir: str) -> Dict[str, Any]:
        """
        Validate audio annotations (CSV format).
        
        Args:
            annotations_path: Path to audio annotations CSV
            audio_dir: Directory containing audio files
            
        Returns:
            Dict containing validation results
        """
        results = {
            'total_samples': 0,
            'missing_audio_files': [],
            'missing_transcriptions': 0,
            'transcription_length_stats': {},
            'duration_stats': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            df = pd.read_csv(annotations_path)
            results['total_samples'] = len(df)
            
            transcription_lengths = []
            durations = []
            
            for _, row in df.iterrows():
                # Check audio file exists
                audio_file = row.get('audio_file', '')
                if audio_file:
                    audio_path = os.path.join(audio_dir, audio_file)
                    if not os.path.exists(audio_path):
                        results['missing_audio_files'].append(audio_file)
                
                # Check transcription
                transcription = row.get('transcription', '')
                if not transcription or (isinstance(transcription, str) and len(transcription.strip()) == 0):
                    results['missing_transcriptions'] += 1
                else:
                    transcription_lengths.append(len(str(transcription)))
                
                # Check duration if available
                duration = row.get('duration', None)
                if duration and isinstance(duration, (int, float)) and duration > 0:
                    durations.append(duration)
            
            # Calculate statistics
            if transcription_lengths:
                results['transcription_length_stats'] = {
                    'min': min(transcription_lengths),
                    'max': max(transcription_lengths),
                    'mean': sum(transcription_lengths) / len(transcription_lengths),
                    'median': sorted(transcription_lengths)[len(transcription_lengths) // 2]
                }
            
            if durations:
                results['duration_stats'] = {
                    'min': min(durations),
                    'max': max(durations),
                    'mean': sum(durations) / len(durations),
                    'total': sum(durations)
                }
            
            # Check for issues
            if len(results['missing_audio_files']) > results['total_samples'] * 0.05:
                results['warnings'].append(f"High percentage of missing audio files: {len(results['missing_audio_files'])}/{results['total_samples']}")
            
        except Exception as e:
            results['errors'].append(f"Failed to validate audio annotations: {str(e)}")
        
        return results

    def generate_qa_report(self, output_path: str, project_name: str = "MultiModal Dataset") -> bool:
        """
        Generate a comprehensive QA report.
        
        Args:
            output_path: Path to save the QA report CSV
            project_name: Name of the project for the report
            
        Returns:
            bool: True if report generated successfully
        """
        try:
            report_data = []
            
            # Add header information
            report_data.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'project_name': project_name,
                'qa_version': '1.0'
            })
            
            # Add results from each modality
            for modality, results in self.qa_results.items():
                for key, value in results.items():
                    report_data.append({
                        'modality': modality,
                        'metric': key,
                        'value': str(value)
                    })
            
            # Save to CSV
            df = pd.DataFrame(report_data)
            df.to_csv(output_path, index=False)
            
            self.log(f"QA report generated: {output_path}")
            return True
            
        except Exception as e:
            self.log(f"Failed to generate QA report: {str(e)}")
            return False

    def run_full_qa_check(self, config: Dict[str, str]) -> Dict[str, Any]:
        """
        Run comprehensive QA check on all modalities.
        
        Args:
            config: Dictionary with paths for different annotation files and directories
                   Expected keys: 'image_annotations', 'images_dir', 'text_annotations', 
                                 'audio_annotations', 'audio_dir'
        
        Returns:
            Dict containing all QA results
        """
        self.log("Starting comprehensive QA check...")
        
        # Image annotations QA
        if 'image_annotations' in config and 'images_dir' in config:
            self.log("Checking image annotations...")
            self.qa_results['images'] = self.validate_image_annotations(
                config['image_annotations'], config['images_dir']
            )
        
        # Text annotations QA
        if 'text_annotations' in config:
            self.log("Checking text annotations...")
            self.qa_results['text'] = self.validate_text_annotations(
                config['text_annotations']
            )
        
        # Audio annotations QA
        if 'audio_annotations' in config and 'audio_dir' in config:
            self.log("Checking audio annotations...")
            self.qa_results['audio'] = self.validate_audio_annotations(
                config['audio_annotations'], config['audio_dir']
            )
        
        self.log("QA check completed!")
        return self.qa_results


def main():
    """Example usage of the AnnotationQAChecker class."""
    qa_checker = AnnotationQAChecker(verbose=True)
    
    # Example configuration
    config = {
        'image_annotations': 'annotations/image_labels.json',
        'images_dir': 'data/images/',
        'text_annotations': 'annotations/text_labels.csv',
        'audio_annotations': 'annotations/audio_labels.csv',
        'audio_dir': 'data/audio/'
    }
    
    # Run QA check (uncomment to test)
    # results = qa_checker.run_full_qa_check(config)
    # qa_checker.generate_qa_report('qa/qa_report.csv')
    
    print("QA Checker initialized. Import this module to use QA functions.")


if __name__ == "__main__":
    main()
