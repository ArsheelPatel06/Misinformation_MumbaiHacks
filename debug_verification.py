"""
Debug script to reproduce Gemini verification error
"""
import asyncio
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

VERIFICATION_PROMPT = """You are an expert fact-checker verifying claims during global crises.

Analyze this claim and determine its veracity:

CLAIM: {claim}

Context:
- Crisis Type: {crisis_type}
- Source: {source}
- Entities: {entities}

Your task:
1. Assess if the claim is TRUE, FALSE, MIXED (partially true), or UNVERIFIABLE
2. Provide confidence score (0.0-1.0)
3. Explain your reasoning with specific evidence
4. Identify what sources would support or contradict this claim

Consider:
- Is this claim factually accurate?
- Are there credible sources that verify or contradict it?
- Is the claim taken out of context?
- Are there any logical fallacies or misleading elements?

Respond in JSON format:
{
  "verdict": "true|false|mixed|unverifiable",
  "confidence": 0.85,
  "reasoning": "detailed explanation of your assessment",
  "supporting_evidence": ["evidence point 1", "evidence point 2"],
  "contradicting_evidence": ["contradiction 1", "contradiction 2"],
  "recommended_sources": ["source type 1", "source type 2"]
}"""

async def debug_verification():
    print("🚀 Starting debug verification...")
    
    claim_text = "5G towers spread coronavirus"
    prompt = VERIFICATION_PROMPT.format(
        claim=claim_text,
        crisis_type="pandemic",
        source="user_submission",
        entities=["5G", "coronavirus"]
    )
    
    print("\n📝 Sending prompt to Gemini...")
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        print("\n🔍 RAW RESPONSE FROM GEMINI:")
        print("-" * 40)
        print(text)
        print("-" * 40)
        print(f"Type: {type(text)}")
        print(f"Length: {len(text)}")
        
        # Try parsing
        print("\n🧩 Attempting to parse...")
        
        # Clean up
        cleaned_text = text.strip()
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0]
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[1].split("```")[0]
            
        print(f"Cleaned text: {cleaned_text[:100]}...")
        
        try:
            result = json.loads(cleaned_text)
            print("\n✅ Parsing SUCCESS!")
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Parsing FAILED: {e}")
            
    except Exception as e:
        print(f"\n❌ Error calling Gemini: {e}")

if __name__ == "__main__":
    asyncio.run(debug_verification())
