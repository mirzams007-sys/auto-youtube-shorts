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
    print("🖼️ Image ban rahi hai...")
    search_term = text.split()[0] # Pehla shabd use karega image ke liye
    image_url = f"https://pollinations.ai/p/space_galaxy_{search_term}?width=1080&height=1920"
    img_data = requests.get(image_url).content
    with open("image.jpg", "wb") as f:
        f.write(img_data)

    # Step 4: Editing
    print("🎬 Video edit ho rahi hai...")
    # Image Clip
    clip = ImageClip("image.jpg").set_duration(audio.duration + 1)
    
    # Text Overlay (Simple)
    txt_clip = TextClip(text, fontsize=50, color='white', font='DejaVu-Sans-Bold', size=(1000, None), method='caption')
    txt_clip = txt_clip.set_position('center').set_duration(audio.duration + 1)

    # Final Combine
    final = CompositeVideoClip([clip, txt_clip]).set_audio(audio)
    final.write_videofile("viral_short.mp4", fps=24, codec="libx264", audio_codec="aac")
    
    print("✅ Video Taiyar hai! Download karein.")

if __name__ == "__main__":
    asyncio.run(make_video())
