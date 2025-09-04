# Edge Cases Documentation

## Image Annotation Edge Cases

### 1. Partial Objects
**Situation**: Object is partially visible at image boundaries
**Decision Rule**: Include if >50% visible, exclude if <50%
**Examples**:
- Car half-cropped at image edge → Include if front/back visible
- Person's head cut off → Exclude, insufficient context

### 2. Reflections and Mirrors
**Situation**: Objects visible through reflections
**Decision Rule**: Annotate as separate instances if clearly identifiable
**Examples**:
- Mirror reflection of person → Separate annotation
- Water reflection → Skip if distorted beyond recognition

### 3. Multiple Scales
**Situation**: Same object type at different scales
**Decision Rule**: Annotate all instances regardless of size
**Examples**:
- Large apple and small apple → Both annotated
- Background and foreground people → All annotated

### 4. Artistic Representations
**Situation**: Drawings, paintings, or sculptures of objects
**Decision Rule**: Treat as the actual object category
**Examples**:
- Drawing of apple → Category: "fruit"
- Statue of person → Category: "person"

## Text Annotation Edge Cases

### 1. Sarcasm Detection
**Situation**: Sarcastic comments with opposite literal meaning
**Decision Rule**: Label based on intended sentiment, not literal
**Examples**:
- "Oh great, another delay!" → negative (not positive)
- "Perfect weather for a picnic" (during storm) → negative

### 2. Mixed Language Content
**Situation**: Text contains multiple languages
**Decision Rule**: Annotate based on dominant language
**Examples**:
- "Hello amigo, ¿cómo estás?" → English (dominant)
- Add language note in metadata

### 3. Abbreviations and Acronyms
**Situation**: Unclear abbreviations or acronyms
**Decision Rule**: Expand only if meaning affects annotation
**Examples**:
- "LOL that's funny" → Keep as-is for sentiment
- "NASA launched rocket" → Expand for NER: "National Aeronautics and Space Administration"

### 4. Emotional Expressions
**Situation**: Emoticons, emojis, or emotional punctuation
**Decision Rule**: Include in sentiment analysis
**Examples**:
- "Okay... :(" → negative sentiment
- "Great!!!" → positive sentiment

## Audio Annotation Edge Cases

### 1. Overlapping Speech
**Situation**: Multiple speakers talking simultaneously
**Decision Rule**: Mark as [Overlap] and transcribe dominant speaker
**Examples**:
- Both speakers audible → "[Overlap: Speaker1] main transcription"
- Background chatter → Focus on primary conversation

### 2. Background Music/Noise
**Situation**: Non-speech audio interfering with transcription
**Decision Rule**: Note in metadata, transcribe speech only
**Examples**:
- Music playing → Note: "background music present"
- Traffic noise → Note: "traffic noise, 0:30-0:45"

### 3. Different Accents/Dialects
**Situation**: Strong accents affecting comprehension
**Decision Rule**: Transcribe intended words, note accent if relevant
**Examples**:
- Strong southern accent → Transcribe standard spelling
- Regional dialect → Note in metadata

### 4. Technical Audio Issues
**Situation**: Echo, distortion, or poor recording quality
**Decision Rule**: Mark unclear sections, describe issue
**Examples**:
- Echo: "Hello [echo] how are you"
- Distortion: "The meeting is [distorted] tomorrow"

## Quality Assessment Edge Cases

### 1. Disagreement Resolution
**Situation**: Annotators disagree on labels
**Decision Rule**: Use majority vote, escalate ties to expert
**Process**:
1. Check guidelines adherence
2. Majority vote (3+ annotators)
3. Expert review for ties
4. Document decision rationale

### 2. Confidence Scoring
**Situation**: Uncertain about annotation quality
**Decision Rule**: Use three-tier confidence system
**Levels**:
- **High**: Clear, unambiguous case
- **Medium**: Some uncertainty, defensible choice
- **Low**: High uncertainty, requires review

### 3. New Category Discovery
**Situation**: Encounter object/concept not in guidelines
**Decision Rule**: Use "other" temporarily, propose new category
**Process**:
1. Use "other" label with description
2. Collect similar cases
3. Propose new category if frequent
4. Update guidelines after review

## Format Conversion Edge Cases

### 1. Missing Metadata
**Situation**: Required fields missing during conversion
**Decision Rule**: Use defaults and log warnings
**Defaults**:
- Image dimensions: 640x480
- Category ID: 0 (unknown)
- Confidence: 0.5 (medium)

### 2. Invalid Coordinates
**Situation**: Bounding box coordinates out of image bounds
**Decision Rule**: Clip to image boundaries and warn
**Examples**:
- Negative coordinates → Set to 0
- Coordinates > image size → Clip to max dimension

### 3. Duplicate Annotations
**Situation**: Same annotation appears multiple times
**Decision Rule**: Keep first occurrence, remove duplicates
**Detection**: Compare all fields (bbox, category, image_id)

## Workflow Edge Cases

### 1. Tool Incompatibility
**Situation**: Annotation tool exports non-standard format
**Decision Rule**: Convert to standard format using scripts
**Solutions**:
- Custom conversion scripts
- Format validation checks
- Standard format enforcement

### 2. Large File Handling
**Situation**: Files too large for annotation tools
**Decision Rule**: Split into manageable chunks
**Process**:
1. Split large files
2. Annotate chunks separately  
3. Merge annotations with offset correction

### 3. Team Coordination
**Situation**: Multiple annotators working on same data
**Decision Rule**: Assign clear file ownership
**Process**:
1. Lock files during annotation
2. Use consistent naming conventions
3. Regular synchronization meetings

## Decision Documentation

All edge case decisions should be documented with:
- Date of decision
- Annotator/reviewer involved
- Rationale for decision
- Examples (if applicable)
- Impact on other annotations

## Escalation Process

For complex edge cases:
1. **Level 1**: Team discussion
2. **Level 2**: Senior annotator review
3. **Level 3**: Domain expert consultation
4. **Level 4**: Project lead decision

## Updates and Revisions

This document should be updated when:
- New edge cases are discovered
- Guidelines change
- Tool capabilities change
- Quality issues are identified

---

**Document Version**: 1.0  
**Last Updated**: 2024-09-04  
**Next Review**: 2024-12-04
