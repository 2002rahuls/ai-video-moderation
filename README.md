# AI-Powered Video Moderation Pipeline

A **production-grade multimodal GenAI system** that automatically moderates long-form user-generated videos using **frame sampling + deterministic LLM reasoning**.
Built for **scalability, reliability, and safety** in real-world platforms.

---

## Problem Statement

Manual moderation of user-uploaded videos does not scale and poses serious risks:

- Unsafe or explicit content exposure
- Non-educational or low-quality submissions
- PII leakage (names, phone numbers, IDs)
- Copyright and platform watermark violations
- High operational cost and delayed review cycles

Traditional rule-based systems fail to understand **visual context across time**.

---

## Solution Overview

This project implements a **GenAI video moderation pipeline** that:

- Samples video frames at fixed intervals using FFmpeg
- Sends visual context to a multimodal LLM (OpenAI GPT-4o)
- Enforces **strict JSON-only outputs** via schema validation
- Applies deterministic moderation rules for K-12 platforms
- Processes videos in **fault-tolerant batches**
- Updates moderation results back to Firestore for downstream systems

The system is designed to behave like a **production AI service**, not a demo.

---

## High-Level Architecture

```
User Video Upload
        ↓
Firestore (FAILED / WAITING)
        ↓
Batch Worker (Async + Thread Pool)
        ↓
FFmpeg Frame Sampling (every N seconds)
        ↓
Multimodal LLM (GPT-4o)
        ↓
Strict JSON Schema Validation
        ↓
Firestore Update + Error Reports
```

---

## Key Engineering Highlights

- **Multimodal reasoning** using sampled video frames
- **Deterministic prompt design** with JSON-only contracts
- **Strict schema enforcement** using Pydantic
- **Self-contained per-video timeouts** (prevents pipeline stalls)
- **Batch processing with concurrency control**
- **Cost-aware inference** via frame and token budgeting
- **Graceful failure handling** with partial success support
- **Cloud-ready** via Docker containerization

---

## Moderation Capabilities

The system evaluates videos for:

- K-12 safety and explicit content
- Educational vs entertainment classification
- STEM relevance detection
- PII exposure (names, phone numbers, IDs)
- Copyright & platform watermark risks
- Visible objects and keywords for auditability

Each video is classified as:

- `approved`
- `needsManualReview`
- `rejected`
- `failed` (timeout / system error)

---

## Tech Stack

- **Python 3.11**
- **FFmpeg** (frame extraction)
- **OpenAI GPT-4o (multimodal)**
- **AsyncIO + ThreadPoolExecutor**
- **Pydantic** (schema validation)
- **Firebase Firestore**
- **Docker**

---

## Project Structure

```
ai-video-moderation/
├── app/
│   ├── worker.py          # Per-video processing logic
│   ├── pipeline.py        # Core AI orchestration
│   ├── firestore.py      # Firestore initialization & helpers
│   │
│   ├── video/
│   │   └── extractor.py  # FFmpeg frame sampling
│   │
│   ├── ai/
│   │   ├── client.py     # OpenAI async client
│   │   ├── prompt.py     # Deterministic moderation prompt
│   │   ├── schema.py     # Strict JSON schema
│   │
│   └── config.py         # Environment-based configuration
│
├── scripts/
│   └── run_batch.py      # Batch execution entrypoint
│
├── tests/
│   └── test_schema.py    # Schema validation test
│
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Configuration

All configuration is environment-based.

### `.env.example`

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

FRAME_INTERVAL=0.1
MAX_FRAMES=30
TIMEOUT_SECONDS=45

BATCH_SIZE=8
GOOGLE_APPLICATION_CREDENTIALS=service-account.json
```

---

## Running Locally

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Set environment variables

```bash
cp .env.example .env
```

### 3️⃣ Run batch moderation

```bash
python scripts/run_batch.py
```

---

## 🐳 Docker Usage

### Build image

```bash
docker build -t ai-video-moderation .
```

### Run container

```bash
docker run --env-file .env ai-video-moderation
```

---

## Testing Strategy

The project follows a **layered testing approach**:

1. **Unit sanity tests**

   - Frame extraction
   - JSON schema validation

2. **Local end-to-end test**

   - Single video moderation without Firestore

3. **Batch integration test**

   - Firestore → AI → Firestore update

4. **Docker runtime validation**

   - Confirms cloud readiness

This ensures correctness, fault tolerance, and production stability.

---

## Why This Project Matters

This is **not** a chatbot or demo.

It demonstrates:

- Real multimodal GenAI usage
- Prompt engineering with deterministic guarantees
- Production-grade fault tolerance
- Cost-aware AI system design
- Cloud-native deployment readiness

The same architecture can be extended to:

- EdTech platforms
- Social media moderation
- Content compliance systems
- Enterprise video pipelines

---

## Future Scope

- **Audio-Aware Moderation**: Extend the pipeline to analyze audio tracks using Speech-to-Text (STT) for detecting inappropriate language, hate speech, bullying, or sensitive disclosures that may not be visible in frames.
- **Multimodal Fusion**: Combine visual signals (frames), textual signals (OCR), and audio transcripts to enable richer, context-aware moderation decisions using LLM-based multimodal reasoning.
- **Confidence Scoring & Explainability**: Introduce confidence scores and explanation traces per modality (visual/audio/text) to improve auditability and human review workflows.
- **Cost-Optimized Inference**: Dynamically adjust frame sampling and audio chunking based on video length, content density, or prior risk signals to reduce inference costs at scale.

---

## Author

**Rahul Shah**
Backend & GenAI Engineer
Focused on building **scalable, reliable AI systems** using cloud-native architectures.
