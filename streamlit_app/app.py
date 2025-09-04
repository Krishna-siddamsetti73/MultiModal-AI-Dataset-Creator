#!/usr/bin/env python3
"""
Multi-Modal Dataset Dashboard

A Streamlit application for visualizing, managing, and exploring multi-modal 
ML training datasets with annotations for images, text, and audio.

Features:
- Dataset overview and statistics
- Data preview and filtering
- Annotation quality analysis
- Format conversion utilities
- Download functionality
- Documentation viewer

Author: MultiModal AI Dataset Creator
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from typing import Dict, List, Any
import sys

# Add the scripts directory to the path for imports
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(script_dir))

try:
    from format_converter import FormatConverter
    from qa_checker import AnnotationQAChecker
    from file_renamer import DatasetFileRenamer
except ImportError:
    st.warning("Some utility scripts are not available. Basic functionality will be limited.")


class MultiModalDashboard:
    """Main dashboard class for the multi-modal dataset."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data"
        self.annotations_path = self.base_path / "annotations"
        self.qa_path = self.base_path / "qa"
        self.docs_path = self.base_path / "docs"
        
    def load_data(self) -> Dict[str, Any]:
        """Load all available data from the project structure."""
        data = {
            'images': [],
            'text': [],
            'audio': [],
            'image_annotations': {},
            'text_annotations': [],
            'audio_annotations': [],
            'qa_log': [],
            'label_agreement': []
        }
        
        # Load image data
        images_dir = self.data_path / "images"
        if images_dir.exists():
            data['images'] = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        
        # Load text data
        text_dir = self.data_path / "text"
        if text_dir.exists():
            data['text'] = list(text_dir.glob("*.txt"))
        
        # Load audio data
        audio_dir = self.data_path / "audio"
        if audio_dir.exists():
            data['audio'] = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
        
        # Load annotations
        image_ann_file = self.annotations_path / "image_labels.json"
        if image_ann_file.exists():
            try:
                with open(image_ann_file) as f:
                    data['image_annotations'] = json.load(f)
            except Exception:
                pass
        
        text_ann_file = self.annotations_path / "text_labels.csv"
        if text_ann_file.exists():
            try:
                data['text_annotations'] = pd.read_csv(text_ann_file)
            except Exception:
                data['text_annotations'] = pd.DataFrame()
        
        audio_ann_file = self.annotations_path / "audio_labels.csv"
        if audio_ann_file.exists():
            try:
                data['audio_annotations'] = pd.read_csv(audio_ann_file)
            except Exception:
                data['audio_annotations'] = pd.DataFrame()
        
        # Load QA data
        qa_log_file = self.qa_path / "qa_log.csv"
        if qa_log_file.exists():
            try:
                data['qa_log'] = pd.read_csv(qa_log_file)
            except Exception:
                data['qa_log'] = pd.DataFrame()
        
        agreement_file = self.qa_path / "label_agreement.csv"
        if agreement_file.exists():
            try:
                data['label_agreement'] = pd.read_csv(agreement_file)
            except Exception:
                data['label_agreement'] = pd.DataFrame()
        
        return data


def setup_page_config():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="MultiModal Dataset Dashboard",
        page_icon="🗂️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


def show_overview_page(dashboard: MultiModalDashboard, data: Dict[str, Any]):
    """Display the dataset overview page."""
    st.title("🗂️ MultiModal Dataset Overview")
    
    # Dataset statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📸 Images",
            value=len(data['images']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="📝 Text Samples", 
            value=len(data['text_annotations']) if isinstance(data['text_annotations'], pd.DataFrame) else 0,
            delta=None
        )
    
    with col3:
        st.metric(
            label="🎵 Audio Files",
            value=len(data['audio']),
            delta=None
        )
    
    with col4:
        total_annotations = 0
        if data['image_annotations']:
            total_annotations += len(data['image_annotations'].get('annotations', []))
        if isinstance(data['text_annotations'], pd.DataFrame):
            total_annotations += len(data['text_annotations'])
        if isinstance(data['audio_annotations'], pd.DataFrame):
            total_annotations += len(data['audio_annotations'])
        
        st.metric(
            label="🏷️ Total Annotations",
            value=total_annotations,
            delta=None
        )
    
    # Dataset composition chart
    if total_annotations > 0:
        st.subheader("📊 Dataset Composition")
        
        composition_data = {
            'Modality': ['Images', 'Text', 'Audio'],
            'Count': [
                len(data['image_annotations'].get('annotations', [])) if data['image_annotations'] else 0,
                len(data['text_annotations']) if isinstance(data['text_annotations'], pd.DataFrame) else 0,
                len(data['audio_annotations']) if isinstance(data['audio_annotations'], pd.DataFrame) else 0
            ]
        }
        
        fig = px.pie(
            values=composition_data['Count'],
            names=composition_data['Modality'],
            title="Annotations by Modality"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Quality Overview
    if isinstance(data['qa_log'], pd.DataFrame) and len(data['qa_log']) > 0:
        st.subheader("🎯 Quality Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality score distribution
            quality_counts = data['qa_log']['quality_score'].value_counts()
            fig = px.bar(
                x=quality_counts.index,
                y=quality_counts.values,
                title="Quality Score Distribution",
                labels={'x': 'Quality Score', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Status distribution
            status_counts = data['qa_log']['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Annotation Status"
            )
            st.plotly_chart(fig, use_container_width=True)


def show_data_preview_page(dashboard: MultiModalDashboard, data: Dict[str, Any]):
    """Display the data preview page."""
    st.title("👁️ Data Preview")
    
    # Modality selection
    modality = st.selectbox(
        "Select modality to preview:",
        ["Images", "Text", "Audio"],
        key="preview_modality"
    )
    
    if modality == "Images":
        show_image_preview(data)
    elif modality == "Text":
        show_text_preview(data)
    elif modality == "Audio":
        show_audio_preview(data)


def show_image_preview(data: Dict[str, Any]):
    """Display image preview with annotations."""
    st.subheader("🖼️ Image Data Preview")
    
    if not data['images']:
        st.warning("No images found in the dataset.")
        return
    
    # Image selection
    image_names = [img.name for img in data['images']]
    selected_image = st.selectbox("Select an image:", image_names)
    
    if selected_image:
        # Find the selected image path
        image_path = None
        for img_path in data['images']:
            if img_path.name == selected_image:
                image_path = img_path
                break
        
        if image_path and image_path.exists():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Display image
                image = Image.open(image_path)
                st.image(image, caption=selected_image, use_column_width=True)
            
            with col2:
                # Display image info
                st.write("**Image Information:**")
                st.write(f"- Filename: {selected_image}")
                st.write(f"- Size: {image.size}")
                st.write(f"- Mode: {image.mode}")
                
                # Display annotations if available
                if data['image_annotations']:
                    annotations = data['image_annotations'].get('annotations', [])
                    image_id = None
                    
                    # Find image ID
                    for img_info in data['image_annotations'].get('images', []):
                        if img_info['file_name'] == selected_image:
                            image_id = img_info['id']
                            break
                    
                    if image_id is not None:
                        img_annotations = [ann for ann in annotations if ann['image_id'] == image_id]
                        if img_annotations:
                            st.write("**Annotations:**")
                            for ann in img_annotations:
                                st.write(f"- Category ID: {ann.get('category_id', 'N/A')}")
                                st.write(f"- BBox: {ann.get('bbox', 'N/A')}")


def show_text_preview(data: Dict[str, Any]):
    """Display text data preview."""
    st.subheader("📝 Text Data Preview")
    
    if isinstance(data['text_annotations'], pd.DataFrame) and len(data['text_annotations']) > 0:
        # Display text annotations
        st.write("**Text Annotations:**")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            if 'label' in data['text_annotations'].columns:
                labels = data['text_annotations']['label'].unique()
                selected_labels = st.multiselect("Filter by label:", labels, default=labels[:5])
            else:
                selected_labels = []
        
        with col2:
            max_samples = st.slider("Max samples to show:", 1, min(100, len(data['text_annotations'])), 10)
        
        # Filter and display data
        filtered_df = data['text_annotations']
        if selected_labels and 'label' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['label'].isin(selected_labels)]
        
        st.dataframe(filtered_df.head(max_samples), use_container_width=True)
        
        # Text statistics
        if 'text' in filtered_df.columns:
            st.write("**Text Statistics:**")
            text_lengths = filtered_df['text'].astype(str).str.len()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Length", f"{text_lengths.mean():.1f}")
            with col2:
                st.metric("Min Length", text_lengths.min())
            with col3:
                st.metric("Max Length", text_lengths.max())
    else:
        st.warning("No text annotations found.")


def show_audio_preview(data: Dict[str, Any]):
    """Display audio data preview."""
    st.subheader("🎵 Audio Data Preview")
    
    if isinstance(data['audio_annotations'], pd.DataFrame) and len(data['audio_annotations']) > 0:
        st.write("**Audio Annotations:**")
        
        # Display audio annotations table
        st.dataframe(data['audio_annotations'], use_container_width=True)
        
        # Audio player for sample files
        if not data['audio'].empty:
            selected_audio = st.selectbox(
                "Select audio file to play:",
                [audio.name for audio in data['audio']]
            )
            
            if selected_audio:
                audio_path = None
                for audio in data['audio']:
                    if audio.name == selected_audio:
                        audio_path = audio
                        break
                
                if audio_path and audio_path.exists():
                    st.audio(str(audio_path))
    else:
        st.warning("No audio annotations found.")


def show_quality_analysis_page(dashboard: MultiModalDashboard, data: Dict[str, Any]):
    """Display quality analysis page."""
    st.title("🎯 Quality Analysis")
    
    if isinstance(data['qa_log'], pd.DataFrame) and len(data['qa_log']) > 0:
        st.subheader("📊 Quality Metrics")
        
        # Quality overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_quality = len(data['qa_log'][data['qa_log']['quality_score'] == 'high'])
            st.metric("High Quality", high_quality)
        
        with col2:
            medium_quality = len(data['qa_log'][data['qa_log']['quality_score'] == 'medium'])
            st.metric("Medium Quality", medium_quality)
        
        with col3:
            low_quality = len(data['qa_log'][data['qa_log']['quality_score'] == 'low'])
            st.metric("Low Quality", low_quality)
        
        with col4:
            completion_rate = len(data['qa_log'][data['qa_log']['status'] == 'completed']) / len(data['qa_log']) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        # Detailed QA log
        st.subheader("📋 QA Log")
        st.dataframe(data['qa_log'], use_container_width=True)
        
        # Inter-annotator agreement
        if isinstance(data['label_agreement'], pd.DataFrame) and len(data['label_agreement']) > 0:
            st.subheader("🤝 Inter-Annotator Agreement")
            
            if 'agreement_score' in data['label_agreement'].columns:
                avg_agreement = data['label_agreement']['agreement_score'].mean()
                st.metric("Average Agreement Score", f"{avg_agreement:.3f}")
            
            st.dataframe(data['label_agreement'], use_container_width=True)
    else:
        st.warning("No quality analysis data available.")


def show_tools_page(dashboard: MultiModalDashboard):
    """Display tools and utilities page."""
    st.title("🛠️ Tools & Utilities")
    
    tab1, tab2, tab3 = st.tabs(["Format Converter", "QA Checker", "File Renamer"])
    
    with tab1:
        show_format_converter_tool(dashboard)
    
    with tab2:
        show_qa_checker_tool(dashboard)
    
    with tab3:
        show_file_renamer_tool(dashboard)


def show_format_converter_tool(dashboard: MultiModalDashboard):
    """Display format converter tool interface."""
    st.subheader("📄 Format Converter")
    
    conversion_type = st.selectbox(
        "Select conversion type:",
        ["COCO to YOLO", "YOLO to COCO", "CSV to JSON", "JSON to CSV"]
    )
    
    if conversion_type in ["COCO to YOLO", "YOLO to COCO"]:
        col1, col2 = st.columns(2)
        with col1:
            input_file = st.text_input("Input file path:")
        with col2:
            output_dir = st.text_input("Output directory:")
        
        if st.button(f"Convert {conversion_type}"):
            if input_file and output_dir:
                try:
                    converter = FormatConverter()
                    if conversion_type == "COCO to YOLO":
                        success = converter.coco_to_yolo(input_file, output_dir)
                    else:
                        success = converter.yolo_to_coco(input_file, "data/images/", output_dir)
                    
                    if success:
                        st.success(f"Conversion completed successfully!")
                    else:
                        st.error("Conversion failed. Check the logs for details.")
                except Exception as e:
                    st.error(f"Error during conversion: {str(e)}")
            else:
                st.warning("Please provide both input file and output directory paths.")


def show_qa_checker_tool(dashboard: MultiModalDashboard):
    """Display QA checker tool interface."""
    st.subheader("🔍 QA Checker")
    
    if st.button("Run Full QA Check"):
        try:
            qa_checker = AnnotationQAChecker()
            
            config = {
                'image_annotations': str(dashboard.annotations_path / "image_labels.json"),
                'images_dir': str(dashboard.data_path / "images"),
                'text_annotations': str(dashboard.annotations_path / "text_labels.csv"),
                'audio_annotations': str(dashboard.annotations_path / "audio_labels.csv"),
                'audio_dir': str(dashboard.data_path / "audio")
            }
            
            results = qa_checker.run_full_qa_check(config)
            
            st.success("QA check completed!")
            st.json(results)
            
            # Save results
            report_path = str(dashboard.qa_path / "qa_report.csv")
            qa_checker.generate_qa_report(report_path)
            st.info(f"QA report saved to: {report_path}")
            
        except Exception as e:
            st.error(f"Error during QA check: {str(e)}")


def show_file_renamer_tool(dashboard: MultiModalDashboard):
    """Display file renamer tool interface."""
    st.subheader("📝 File Renamer")
    
    file_type = st.selectbox("Select file type:", ["Images", "Audio"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        prefix = st.text_input("Prefix:", value="img" if file_type == "Images" else "audio")
    with col2:
        start_index = st.number_input("Start index:", value=1, min_value=1)
    with col3:
        zero_padding = st.number_input("Zero padding:", value=4, min_value=1, max_value=6)
    
    if st.button(f"Rename {file_type}"):
        try:
            renamer = DatasetFileRenamer()
            
            if file_type == "Images":
                results = renamer.rename_images_systematic(
                    str(dashboard.data_path / "images"), prefix, start_index, zero_padding
                )
            else:
                results = renamer.rename_audio_systematic(
                    str(dashboard.data_path / "audio"), prefix, start_index, zero_padding
                )
            
            if results:
                st.success(f"Renamed {len(results)} files successfully!")
                st.json(results)
            else:
                st.warning("No files were renamed.")
                
        except Exception as e:
            st.error(f"Error during file renaming: {str(e)}")


def show_documentation_page(dashboard: MultiModalDashboard):
    """Display documentation page."""
    st.title("📚 Documentation")
    
    doc_type = st.selectbox(
        "Select documentation:",
        ["Annotation Guidelines", "README", "Project Structure"]
    )
    
    if doc_type == "Annotation Guidelines":
        guidelines_path = dashboard.docs_path / "annotation_guidelines.md"
        if guidelines_path.exists():
            with open(guidelines_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.markdown(content)
        else:
            st.error("Annotation guidelines not found.")
    
    elif doc_type == "README":
        readme_path = dashboard.base_path / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.markdown(content)
        else:
            st.error("README file not found.")
    
    elif doc_type == "Project Structure":
        st.markdown("""
        ## 📁 Project Structure
        
        ```
        MultiModal-AI-Dataset-Creator/
        │
        ├── data/
        │   ├── images/          # Raw image files
        │   ├── text/           # Text samples
        │   └── audio/          # Audio files
        │
        ├── annotations/
        │   ├── image_labels.json    # Image annotations
        │   ├── text_labels.csv      # Text annotations
        │   └── audio_labels.csv     # Audio annotations
        │
        ├── scripts/
        │   ├── format_converter.py  # Format conversion utilities
        │   ├── qa_checker.py        # Quality assurance tools
        │   └── file_renamer.py      # File management tools
        │
        ├── qa/
        │   ├── qa_log.csv          # QA tracking
        │   └── label_agreement.csv # Inter-annotator agreement
        │
        ├── docs/
        │   └── annotation_guidelines.md
        │
        └── streamlit_app/
            └── app.py              # This dashboard
        ```
        """)


def main():
    """Main application entry point."""
    setup_page_config()
    
    # Initialize dashboard
    dashboard = MultiModalDashboard()
    
    # Sidebar navigation
    st.sidebar.title("🗂️ MultiModal Dataset")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigate to:",
        [
            "📊 Overview",
            "👁️ Data Preview", 
            "🎯 Quality Analysis",
            "🛠️ Tools",
            "📚 Documentation"
        ]
    )
    
    # Load data
    with st.spinner("Loading dataset..."):
        data = dashboard.load_data()
    
    # Display selected page
    if page == "📊 Overview":
        show_overview_page(dashboard, data)
    elif page == "👁️ Data Preview":
        show_data_preview_page(dashboard, data)
    elif page == "🎯 Quality Analysis":
        show_quality_analysis_page(dashboard, data)
    elif page == "🛠️ Tools":
        show_tools_page(dashboard)
    elif page == "📚 Documentation":
        show_documentation_page(dashboard)
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Project Info:**")
    st.sidebar.markdown(f"📸 Images: {len(data['images'])}")
    st.sidebar.markdown(f"📝 Text: {len(data['text_annotations']) if isinstance(data['text_annotations'], pd.DataFrame) else 0}")
    st.sidebar.markdown(f"🎵 Audio: {len(data['audio'])}")


if __name__ == "__main__":
    main()
