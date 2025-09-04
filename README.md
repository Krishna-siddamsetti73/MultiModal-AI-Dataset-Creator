# MultiModal AI Dataset Creator

A comprehensive toolkit for creating professional-grade ML training datasets with annotations for multiple modalities including image classification, object detection, text sentiment analysis, NER, and audio transcription.

## 🎯 Project Overview

This project demonstrates the complete workflow of creating a multi-modal ML dataset from scratch using industry-standard annotation tools and best practices. The project includes:

- **Multi-modal data collection** (Images, Text, Audio)
- **Professional annotation workflows** using tools like LabelImg, Doccano, CVAT, and Label Studio
- **Quality assurance practices** with tracking and validation
- **Format conversions** (COCO ↔ YOLO ↔ CSV)
- **Comprehensive documentation** and annotation guidelines
- **Interactive dashboard** built with Streamlit

## 🛠️ Tools Used

### Annotation Tools
- **Label Studio**: Image classification, Intent classification
- **LabelImg**: Object detection (bounding boxes)
- **CVAT**: Semantic segmentation
- **Doccano**: Sentiment analysis, NER
- **Audacity**: Audio transcription (manual)

### Development Stack
- **Python**: Data processing and format conversion
- **Streamlit**: Interactive dashboard
- **Excel/CSV**: QA tracking and reporting
- **Git**: Version control

## 📁 Project Structure

```
MultiModal-AI-Dataset-Creator/
│
├── data/
│   ├── images/          # Raw image files
│   ├── text/           # Text samples (reviews, comments)
│   └── audio/          # Audio files (WAV format)
│
├── annotations/
│   ├── image_labels.json    # Image annotations (COCO format)
│   ├── text_labels.csv      # Text annotations
│   └── audio_labels.csv     # Audio transcriptions
│
├── scripts/
│   ├── format_converter.py  # Convert between annotation formats
│   ├── qa_checker.py        # Quality assurance validation
│   └── file_renamer.py      # Systematic file naming
│
├── qa/
│   ├── qa_log.csv          # Quality assurance tracking
│   └── label_agreement.csv  # Inter-annotator agreement
│
├── docs/
│   ├── annotation_guidelines.md  # Annotation standards
│   ├── edge_cases.md             # Edge case documentation
│   └── summary_report.pdf        # Final project report
│
├── streamlit_app/
│   └── app.py              # Interactive dashboard
│
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd MultiModal-AI-Dataset-Creator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the Streamlit dashboard:
```bash
streamlit run streamlit_app/app.py
```

## 📊 Dataset Types

### 🖼️ Image Data
- **Classification**: Fruits, tools, signboards (50-100 images)
- **Object Detection**: Bounding box annotations
- **Segmentation**: Pixel-level annotations
- **Formats**: COCO JSON, YOLO TXT, CSV

### 📄 Text Data
- **Sentiment Analysis**: Product reviews, social media comments
- **NER**: Named entity recognition
- **Intent Classification**: User queries and intents
- **Formats**: JSON, CSV, CoNLL

### 🔊 Audio Data
- **Transcription**: Speech-to-text
- **Speaker Diarization**: Speaker identification
- **Formats**: WAV, CSV annotations

## 🔍 Quality Assurance

- **Validation Scripts**: Automated consistency checking
- **QA Tracking**: Excel-based progress monitoring
- **Gold Standard**: Reference annotations for validation
- **Edge Case Documentation**: Handling of ambiguous cases

## 📈 Usage Examples

### Format Conversion
```python
from scripts.format_converter import convert_coco_to_yolo
convert_coco_to_yolo('annotations/image_labels.json', 'output/')
```

### Quality Check
```python
from scripts.qa_checker import validate_annotations
validate_annotations('annotations/', 'qa/qa_log.csv')
```

## 🤝 Contributing

1. Follow the annotation guidelines in `docs/annotation_guidelines.md`
2. Use the QA checklist for validation
3. Document edge cases and decisions
4. Update the QA log for all changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

For questions about annotation guidelines or dataset usage, please refer to the documentation in the `docs/` folder or create an issue in this repository.
Linkedin : https://www.linkedin.com/in/krishna-siddamsetti-045862290/
mail: krishnasiddamsetti15@gmail.com

