# Multi-Modal Dataset Annotation Guidelines

## Table of Contents
1. [General Guidelines](#general-guidelines)
2. [Image Annotations](#image-annotations)
3. [Text Annotations](#text-annotations)
4. [Audio Annotations](#audio-annotations)
5. [Quality Standards](#quality-standards)
6. [Edge Cases](#edge-cases)
7. [Tools and Workflows](#tools-and-workflows)

---

## General Guidelines

### Annotation Principles
- **Consistency**: Apply the same criteria across all similar cases
- **Accuracy**: Double-check all annotations before submitting
- **Completeness**: Annotate all required elements in each sample
- **Documentation**: Record any ambiguous cases or special decisions

### File Naming Conventions
- Use systematic naming: `[type]_[index].[extension]`
- Zero-pad indices: `img_0001.jpg`, `audio_0001.wav`
- Use lowercase for consistency
- No spaces in filenames (use underscores)

### Annotation Format Standards
- **Images**: COCO JSON format for object detection, CSV for classification
- **Text**: CSV with `text` and `label` columns, JSON for complex structures
- **Audio**: CSV with `audio_file`, `transcription`, and metadata columns

---

## Image Annotations

### 🖼️ Image Classification

**Objective**: Assign a single primary label to each image

**Categories**:
- `fruit`: Apples, oranges, bananas, etc.
- `tool`: Hammer, screwdriver, wrench, etc.
- `signboard`: Traffic signs, store signs, warning signs

**Guidelines**:
1. Choose the most prominent object in the image
2. If multiple objects are present, label the largest/most central one
3. Use `mixed` label if no single object dominates (>60% of image)
4. Use `unclear` if the image quality prevents confident classification

**Example**:
```csv
filename,label,confidence,notes
img_0001.jpg,fruit,high,Clear apple in center
img_0002.jpg,tool,medium,Partially visible hammer
img_0003.jpg,mixed,low,Multiple small tools
```

### 🎯 Object Detection (Bounding Boxes)

**Objective**: Locate and classify all objects of interest in the image

**Bounding Box Rules**:
- Draw tight boxes around objects (minimal background)
- Include partial objects if >50% is visible
- Use rectangular boxes aligned with image axes
- Minimum box size: 10x10 pixels

**Class Labels**:
- Use specific labels: `red_apple`, `green_apple` rather than just `apple`
- Maintain consistent naming within categories
- Create new labels for distinct object types

**Quality Criteria**:
- Box edges should align with object boundaries
- No significant background inside the box
- Multiple boxes for multiple instances of same class
- Overlapping boxes are acceptable if objects overlap

**COCO Format Example**:
```json
{
  "id": 1,
  "image_id": 1,
  "category_id": 1,
  "bbox": [100, 150, 200, 180],
  "area": 36000,
  "iscrowd": 0
}
```

### 🎨 Semantic Segmentation

**Objective**: Pixel-level classification of image regions

**Guidelines**:
- Annotate at pixel level, not bounding boxes
- Use different colors for different classes
- Include background as a separate class
- Be precise at object boundaries

**Classes**:
- `background`: Everything not of interest
- `object`: The main object class
- `shadow`: Object shadows (if relevant)

---

## Text Annotations

### 📝 Sentiment Analysis

**Objective**: Classify the emotional sentiment of text samples

**Labels**:
- `positive`: Clearly positive sentiment
- `negative`: Clearly negative sentiment  
- `neutral`: No clear sentiment or balanced
- `mixed`: Contains both positive and negative elements

**Guidelines**:
1. Consider the overall tone, not individual words
2. Context matters - consider domain-specific expressions
3. Sarcasm should be labeled based on intent, not literal meaning
4. When uncertain, use `neutral` rather than guessing

**Examples**:
```csv
text,label,confidence,notes
"Love this product!",positive,high,Clear positive expression
"Not the worst I've tried",positive,medium,Understated positive
"It's okay I guess",neutral,high,Indifferent tone
"Great product, shame about delivery",mixed,medium,Mixed sentiment
```

### 🏷️ Named Entity Recognition (NER)

**Objective**: Identify and classify named entities in text

**Entity Types**:
- `PERSON`: Names of people
- `ORGANIZATION`: Companies, institutions
- `LOCATION`: Cities, countries, addresses
- `DATE`: Specific dates and times
- `PRODUCT`: Product names and models
- `MONEY`: Monetary amounts

**Annotation Format**:
- Use BIO tagging: B- (beginning), I- (inside), O- (outside)
- Tag at word level
- Include context for ambiguous cases

**Example**:
```
John    B-PERSON
Smith   I-PERSON
works   O
at      O
Apple   B-ORGANIZATION
Inc.    I-ORGANIZATION
```

### 💬 Intent Classification

**Objective**: Classify the intended action or purpose of user queries

**Intent Categories**:
- `question`: Seeking information
- `request`: Asking for action
- `complaint`: Expressing dissatisfaction
- `compliment`: Expressing praise
- `other`: None of the above

**Guidelines**:
- Focus on what the user wants to achieve
- Consider implicit intents (politeness markers)
- Use context from conversation if available

---

## Audio Annotations

### 🎤 Speech Transcription

**Objective**: Convert speech to accurate text representation

**Transcription Rules**:
1. Use exact words spoken (including filler words like "um", "uh")
2. Indicate unclear speech with [inaudible]
3. Use standard punctuation
4. Normalize numbers: "twenty-one" not "21"
5. Include natural pauses with commas

**Format Guidelines**:
- Start/end times in seconds: `00:12.5-00:15.8`
- Speaker identification: `[Speaker1]`, `[Speaker2]`
- Non-speech sounds: `[cough]`, `[laughter]`, `[music]`

**Example**:
```csv
audio_file,start_time,end_time,speaker,transcription,confidence
audio_0001.wav,0.0,3.2,Speaker1,"Hello, how are you today?",high
audio_0001.wav,3.5,5.1,Speaker2,"I'm doing well, thanks for asking.",high
audio_0002.wav,0.0,2.8,Speaker1,"Um, can you help me with [inaudible]?",medium
```

### 👥 Speaker Diarization

**Objective**: Identify who is speaking when

**Speaker Labels**:
- Use consistent speaker IDs: `Speaker1`, `Speaker2`, etc.
- Maintain same ID for same person throughout recording
- Use `[Overlap]` for simultaneous speech
- Use `[Unknown]` for unidentifiable speakers

**Guidelines**:
- Split at natural speech boundaries
- Minimum segment length: 1 second
- Mark overlapping speech clearly
- Note voice characteristics in metadata

---

## Quality Standards

### ⭐ Annotation Quality Levels

**High Quality** (Target: 95% of annotations):
- Clear, unambiguous cases
- High annotator confidence
- Follows guidelines precisely
- Consistent with similar cases

**Medium Quality** (Acceptable: up to 5%):
- Minor ambiguity resolved reasonably
- Some uncertainty but defensible choice
- Slight deviation from guidelines with justification

**Low Quality** (Requires review):
- High ambiguity or uncertainty
- Inconsistent with guidelines
- Potential errors or missing information

### 🔍 Quality Assurance Process

1. **Self-Review**: Check your own work before submission
2. **Peer Review**: Have another annotator verify complex cases
3. **Validation**: Use automated checks where possible
4. **Gold Standard**: Compare against reference annotations
5. **Inter-Annotator Agreement**: Measure consistency across annotators

---

## Edge Cases

### 🤔 Common Ambiguous Situations

#### Images
- **Partial objects**: Include if >50% visible, exclude if <50%
- **Reflections**: Annotate as separate instance if clearly visible
- **Artistic representations**: Treat as the actual object (drawing of apple = apple)
- **Multiple scales**: Annotate all instances regardless of size differences

#### Text
- **Sarcasm**: Label based on intended meaning, not literal interpretation
- **Code-switching**: Handle each language separately if guidelines exist
- **Typos/errors**: Transcribe as written, note in comments if needed
- **Abbreviations**: Expand only if meaning is unclear

#### Audio
- **Background noise**: Include if it affects comprehension
- **Multiple conversations**: Prioritize foreground conversation
- **Different languages**: Note language in metadata
- **Technical issues**: Mark affected regions clearly

### 📋 Decision Trees for Common Cases

#### Uncertain Image Classification:
1. Can you identify the primary object? → Yes: Use specific label
2. Are there multiple equal objects? → Yes: Use `mixed`
3. Is image quality too poor? → Yes: Use `unclear`
4. Still uncertain? → Use `other` with explanation

#### Ambiguous Sentiment:
1. Is there clear emotional language? → Use appropriate sentiment
2. Is the context positive/negative? → Weight context heavily
3. Mixed positive and negative? → Use `mixed`
4. No emotional indicators? → Use `neutral`

---

## Tools and Workflows

### 🛠️ Recommended Annotation Tools

#### Image Annotation:
- **Label Studio**: Web-based, supports multiple formats
- **LabelImg**: Desktop app for bounding boxes
- **CVAT**: Advanced tool for segmentation
- **Roboflow**: Cloud-based with team collaboration

#### Text Annotation:
- **Doccano**: Open-source text annotation platform  
- **Label Studio**: Also supports text annotation
- **Prodigy**: Commercial tool with active learning
- **Custom scripts**: For simple CSV-based annotation

#### Audio Annotation:
- **Audacity**: Free audio editor with labeling
- **Praat**: Phonetics software with transcription tools
- **Label Studio**: Web-based audio annotation
- **ELAN**: Specialized for linguistic annotation

### 📊 Quality Tracking

Use the provided QA tracking templates:
- `qa/qa_log.csv`: Track annotation progress and issues
- `qa/label_agreement.csv`: Measure inter-annotator agreement

### 🔄 Annotation Workflow

1. **Setup**: Install tools, create working directory
2. **Familiarization**: Read guidelines, practice on sample data
3. **Batch Processing**: Annotate in consistent batches
4. **Quality Check**: Run automated validation scripts
5. **Review**: Check edge cases and difficult examples
6. **Submit**: Export in required format
7. **Feedback**: Incorporate QA feedback for next batch

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|---------|
| 2024-01-01 | 1.0 | Initial guidelines created | MultiModal Team |
| 2024-01-15 | 1.1 | Added edge cases section | MultiModal Team |
| 2024-02-01 | 1.2 | Updated NER guidelines | MultiModal Team |

---

**For questions or clarifications, create an issue in the project repository or contact the annotation team lead.**
