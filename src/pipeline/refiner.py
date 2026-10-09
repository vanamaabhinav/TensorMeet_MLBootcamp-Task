from google import genai
from google.genai import types

class TranscriptRefiner:
    def __init__(self):
        self.client = genai.Client()
        self.model_id = "gemini-3.5-flash-lite"

    def refine(self, raw_transcript: str) -> str:
        prompt = f"""
You are a domain-aware transcript refinement AI.
Your task is to correct likely phonetic errors, technical jargon, acronyms, and product names in the provided raw transcript.
You MUST preserve the speaker's original intent, speaker identity (if any), negation, numbers, and commitments.
Do NOT hallucinate new information, and do NOT change the formatting unnecessarily.
Only fix transcription mistakes.

Raw Transcript:
{raw_transcript}
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            )
        )
        return response.text.strip()
