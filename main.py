import os
import asyncio
import requests
import random
import urllib.parse
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip

# API Key
API_KEY = os.getenv("GEMINI_API_KEY")

# Topics jo visual mein acche lagte hain
TOPICS = [
    "Amazing fact about Black Holes",
    "Why Mars is Red",
    "How big is the Sun",
    "Pyramids mystery",
    "Deep sea scary fact"
]

def get_content():
    """Gemini se Hindi Fact aur English Image Prompt lena"""
    topic = random.choice(TOPICS)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # Hum AI ko bolenge: Hindi Text | English Image Description
    prompt = f"Tell me a viral short fact about '{topic}'. Format: Hindi Text (max 15 words) | Short English Visual Description for Image Gen. No emojis."
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text']
        
        # Split karna (Hindi | English)
        if "|" in raw_text:
            hindi_text, img_prompt = raw_text.split("|")
        else:
            hindi_text = raw_text
            img_prompt = topic # Fallback
            
        return hindi_text.strip(), img_prompt.strip()
    except Exception as e:
        print(f"⚠️ Content Error: {e}")
        return "Antariksh bahut bada hai.", "galaxy space stars 8k wallpaper"

async def make_video():
    print("🚀 Auto-Machine Started...")

    # 1. Content
    hindi_text, img_prompt = get_content()
    print(f"📜 Text: {hindi_text}")
    print(f"🖼️ Prompt: {img_prompt}")

    # 2. Audio
    print("🎙️ Generating Voice...")
    await Communicate(hindi_text, "hi-IN-MadhurNeural").save("audio.mp3")
    audio = AudioFileClip("audio.mp3")

    # 3. Image (FIXED METHOD)
    print("🖼️ Generating Image...")
    
    # URL ko safe banana (Spaces ko %20 mein badalna)
    encoded_prompt = urllib.parse.quote(f"hyper realistic 8k, {img_prompt}, cinematic lighting, vertical ratio")
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&model=flux"
    
    try:
        response = requests.get(image_url, timeout=30) # Time badha diya
        if response.status_code == 200 and len(response.content) > 1000:
            with open("image.jpg", "wb") as f:
                f.write(response.content)
            print("✅ Image Saved Successfully!")
        else:
            raise Exception("Image download failed or file too small")
            
    except Exception as e:
        print(f"❌ IMAGE ERROR: {e}")
        # Agar fail ho to ek fix landscape image utha lo (Backup)
        img_data = requests.get("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1080").content
        with open("image.jpg", "wb") as f: f.write(img_data)

    # 4. Editing
    print("🎬 Editing Video...")
    
    # Image Motion Effect (Zoom in) - Thoda advanced look ke liye
    clip = ImageClip("image.jpg").set_duration(audio.duration + 1.5)
    
    # Text Overlay
    txt_clip = TextClip(hindi_text, fontsize=55, color='yellow', stroke_color='black', stroke_width=2, font='DejaVu-Sans-Bold', size=(900, None), method='caption')
    txt_clip = txt_clip.set_position('center').set_duration(audio.duration + 1.5)

    final = CompositeVideoClip([clip, txt_clip]).set_audio(audio)
    final.write_videofile("viral_short.mp4", fps=24, codec="libx264", audio_codec="aac")
    print("✅ VIDEO READY!")

if __name__ == "__main__":
    asyncio.run(make_video())
