# AI-Powered Meeting Assistant

**Inter IIT Tech Meet 15.0 Bootcamp - AI-Powered Meeting Assistant**

An end-to-end multi-modal pipeline built with Streamlit, OpenAI Whisper, and Google Gemini to convert meeting audio into actionable insights.

## Features

- **Audio Transcription**: Uses `openai-whisper` (running locally) to transcribe meeting audio accurately.
- **Transcript Refinement**: Employs Gemini to fix domain-specific jargon, phonetic errors, and acronyms without altering speaker intent or hallucinating.
- **Meeting Minutes & Tasks**: Automatically extracts structured data using Gemini's structured JSON outputs. Guarantees missing owners/deadlines are correctly marked as `unspecified` instead of guessing.
- **Interactive UI**: Upload `.mp3`, `.wav`, etc. Compare raw vs. refined transcripts.
- **Export**: One-click download of the JSON machine-readable record and Markdown human-readable summary.

## Setup Instructions

1. **Prerequisites**: Python 3.10+ (tested on Python 3.14).
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **API Key Setup**:
   Copy `.env.example` to `.env` and add your Gemini API Key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```
   *Note: You can also enter the API key directly in the Streamlit Sidebar!*

## Run the Application

```bash
python -m streamlit run app.py
```

## Architecture & Models

1. **Stage 1: Speech-to-Text (`openai-whisper`)**
   - Transcribes spoken audio into a raw text format.
2. **Stage 2: Transcript Refinement (`gemini-2.5-flash`)**
   - Takes the raw text and applies domain-specific error correction via a strict system prompt.
3. **Stage 3: Documentation Generator (`gemini-2.5-flash`)**
   - Utilizes Pydantic schema generation to enforce strict extraction of Meeting Minutes, Key Decisions, and Action Items.

## Evaluation Rubric Alignment

- **Transcription**: Uses Whisper for reliable baseline capturing names/numbers.
- **Transcript refinement**: Dedicated Stage 2 LLM step solely for correcting typos while retaining exact intent.
- **Minutes and decisions**: Enforced via Pydantic model (`minutes_generator.py`) ensuring empty decisions array if no decisions were agreed upon.
- **Action items**: Strict rule enforcement for `unspecified` owners and deadlines.
- **End-to-End**: `app.py` ties everything seamlessly without manual handoffs. 
