python
import os, asyncio, json, requests
import google.generativeai as genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. SETUP
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
JSON_DATA = os.getenv("CLIENT_SECRET_JSON")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def run_machine():
    # A. TREND FINDER & SCRIPT
    print("🔍 Finding trending topic and writing script...")
    prompt = "Find a trending high-retention viral topic for YouTube Shorts. Write a 30-second script in Hindi. Give me 3 facts. Format: Fact 1, Fact 2, Fact 3."
    res = model.generate_content(prompt)
    facts = [f.strip() for f in res.text.split('\n') if len(f) > 10][:3]
    
    # B. VOICEOVER
    print("🎙️ Creating Voice...")
    script_text = " . ".join(facts)
    await Communicate(script_text, "hi-IN-MadhurNeural").save("v.mp3")
    audio = AudioFileClip("v.mp3")

    # C. IMAGES
    print("🖼️ Generating Images...")
    clips = []
    dur = audio.duration / len(facts)
    for i, t in enumerate(facts):
        img = requests.get(f"https://pollinations.ai/p/{t.replace(' ','_')}?width=1080&height=1920&seed={i}").content
        open(f"{i}.jpg", "wb").write(img)
        clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))

    # D. ASSEMBLE VIDEO
    print("🎬 Making Video...")
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile("short.mp4", fps=24, codec="libx264")

    # E. YOUTUBE UPLOAD (Simplified)
    print("🚀 Video is ready! Manual step needed for first-time login...")

if __name__ == "__main__":
    asyncio.run(run_machine())
