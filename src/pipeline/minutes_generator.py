from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    description: str = Field(description="Actionable task statement.")
    owner: str = Field(description="Spoken assignee name, or 'unspecified' if not explicitly stated.")
    deadline: str = Field(description="Spoken timeframe/date, or 'unspecified' if not explicitly stated.")

class MeetingRecord(BaseModel):
    summary: str = Field(description="High-level synopsis of the meeting.")
    minutes: list[str] = Field(description="Organized bullet points covering main discussion themes.")
    decisions: list[str] = Field(description="Formal list of agreed resolutions. Empty list if none.")
    action_items: list[ActionItem] = Field(description="List of actionable tasks.")

class MeetingDocumentationGenerator:
    def __init__(self, api_key=None):
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()
        self.model_id = "gemini-3.5-flash-lite"

    def generate(self, refined_transcript: str) -> MeetingRecord:
        prompt = f"""
You are an AI meeting assistant. Generate a structured meeting record from the refined transcript below.

CRITICAL RULES:
1. ONLY extract action items if they are clearly assigned.
2. If an action item lacks a specific owner, set 'owner' to 'unspecified'.
3. If an action item lacks a specific deadline, set 'deadline' to 'unspecified'.
4. Do NOT invent or infer decisions if they were merely proposals.

Refined Transcript:
{refined_transcript}
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MeetingRecord,
                temperature=0.1,
            )
        )
        
        return MeetingRecord.model_validate_json(response.text)
