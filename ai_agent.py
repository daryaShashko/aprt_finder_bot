import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logging.warning("GOOGLE_API_KEY not found in environment variables. AI features will fail.")
else:
    genai.configure(api_key=api_key)

# System prompt is passed as part of the content or system instruction if supported.
# For 1.5 Flash, we can often just prepend it to the user message or use system_instruction if using the beta client, 
# but for stability in standard usage, we'll put it in the prompt.
SYSTEM_PROMPT = """
You are an intelligent real estate assistant. Your task is to extract specific information from a Polish real estate rental ad.
Output a valid JSON object with the following keys:
- "total_cost": The estimated total monthly cost (Rent + Admin Fee/Czynsz + Media/Utilities). If a range or uncertain, provide a best estimate string.
- "deposit": The security deposit amount.
- "pets_allowed": Boolean (true/false). Look for keywords like "zwierzęta mile widziane" (allowed) or "bez zwierząt" (not allowed). If not mentioned, set to null or false.
- "summary_ru": A 1-sentence summary of the apartment in Russian.

Ensure the output is pure JSON without markdown code blocks.
"""

def analyze_ad(ad_text: str) -> Optional[Dict[str, Any]]:
    """
    Analyzes the ad text using Gemini 1.5 Flash and returns structured data.
    """
    if not api_key:
        logging.error("Cannot analyze ad: API key missing.")
        return None

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nAd Text:\n{ad_text}"
        
        response = model.generate_content(full_prompt)
        
        if response.text:
            # Clean up potential markdown formatting from Gemini
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            return json.loads(cleaned_text)
        else:
            logging.warning("Gemini returned empty response.")
            return None

    except Exception as e:
        logging.error(f"Error during AI analysis: {e}")
        return None
