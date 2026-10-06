from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv() # Actually load the .env file

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def generate_learning_plan(skills):

    try:

        prompt = f"""

User skills and progress:

{skills}

Create a 7-day focused learning & productivity plan.
Keep it short,actionable, and motivating.
"""
        



        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages = [

                 {"role":"system","content":"You are a productivity coach."},
                 
                 {"role":"user","content": prompt}
            ],
            temperature=0.6,
        )



        return response.choices[0].message.content
    
    except Exception as e:

          # 🔁 Fallback when GPT fails
        return "⚠ AI unavailable. Focus on completing 1 task per skill daily."