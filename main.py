import os
import asyncio
import requests
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip

# 1. API Setup
API_KEY = os.getenv("GEMINI_API_KEY")

def get_fact():
    """Google Gemini se fact mangwana"""
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
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return "Antariksh mein awaaz nahi hoti kyunki wahan hawa nahi hai."
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return "Antariksh mein awaaz nahi hoti kyunki wahan hawa nahi hai."

async def make_video():
    print("🚀 Machine Start ho gayi hai...")

    # Step 1: Content
    text = get_fact()
    print(f"📝 Text: {text}")

    # Step 2: Audio
    print("🎙️ Audio ban raha hai...")
    await Communicate(text, "hi-IN-MadhurNeural").save("audio.mp3")
    audio = AudioFileClip("audio.mp3")

    # Step 3: Image (Fixed & Safe)
    print("🖼️ Image dhoond rahe hain...")
    try:
        # Text saaf karke URL banana
        clean_text = "".join(e for e in text if e.isalnum())[:50] # Sirf shuru ke words lenge taaki link chota rahe
        image_url = f"https://image.pollinations.ai/prompt/realistic_space_universe_{clean_text}?width=1080&height=1920&nologo=true"
        
        response = requests.get(image_url, timeout=20)
        
        if response.status_code == 200:
            with open("image.jpg", "wb") as f:
                f.write(response.content)
            print("✅ Image Downloaded!")
            clip = ImageClip("image.jpg").set_duration(audio.duration + 1)
        else:
            raise Exception("Image download failed")
            
    except Exception as e:
        print(f"⚠️ Image Error: {e}. Using Black Screen.")
        # Agar image fail ho to Black Background use karega (Crash nahi hoga)
        clip = ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(audio.duration + 1)

    # Step 4: Final Editing
    print("🎬 Video Jod rahe hain...")
    
    # Text Overlay (Subtitle)
    # Font size thoda chota kiya hai taaki screen se bahar na jaye
    txt_clip = TextClip(text, fontsize=50, color='white', font='DejaVu-Sans-Bold', size=(1000, None), method='caption')
    txt_clip = txt_clip.set_position('center').set_duration(audio.duration + 1)

    # Combine Image + Text + Audio
    final = CompositeVideoClip([clip, txt_clip]).set_audio(audio)
    
    # Export
    final.write_videofile("viral_short.mp4", fps=24, codec="libx264", audio_codec="aac")
    print("✅ MUBARAK HO! Video ban gayi: viral_short.mp4")

if __name__ == "__main__":
    asyncio.run(make_video())
