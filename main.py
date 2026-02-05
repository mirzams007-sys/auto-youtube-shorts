import os
import asyncio
import requests
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# 1. API Setup (Direct Method - No Library Needed)
API_KEY = os.getenv("GEMINI_API_KEY")

def get_fact():
    """Google Gemini se fact mangwane ka direct tareeka"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": "Tell me one interesting viral fact about space in Hindi. Under 20 words. No intro."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        return text.strip()
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return "Antariksh mein awaaz nahi hoti kyunki wahan hawa nahi hai."

async def make_video():
    print("🚀 Machine Start ho gayi hai...")

    # Step 1: Content
    text = get_fact()
    print(f"📝 Text: {text}")

    # Step 2: Audio (Voice)
    print("🎙️ Audio ban raha hai...")
    await Communicate(text, "hi-IN-MadhurNeural").save("audio.mp3")
    audio = AudioFileClip("audio.mp3")

    # Step 3: Image (AI Image)
    print("🖼️ Step 3: Generating Images...")
        clips = []
        dur = audio.duration / len(facts)
        for i, t in enumerate(facts):
            # URL fix aur Safai
            clean_t = "".join(e for e in t if e.isalnum())
            # Naya URL jo fast hai aur direct image deta hai
            url = f"https://image.pollinations.ai/prompt/space_fact_{clean_t}?width=1080&height=1920&nologo=true"
            
            # Request bhejna
            response = requests.get(url)
            
            # Check karna ke image aayi ya nahi
            if response.status_code == 200:
                with open(f"{i}.jpg", "wb") as f: 
                    f.write(response.content)
                # Image ko clip banana
                clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))
            else:
                # Agar image fail ho jaye to Black Screen laga dega (Error nahi dega)
                print(f"⚠️ Image {i} fail ho gayi, color use kar rahe hain.")
                from moviepy.editor import ColorClip
                clips.append(ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(dur).set_fps(24))
