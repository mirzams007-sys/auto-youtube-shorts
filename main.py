import os
import asyncio
import requests
import random
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip

# API Setup
API_KEY = os.getenv("GEMINI_API_KEY")

# Viral Topics (Cute & Funny)
TOPICS = [
    "A cute fluffy cat trying to cook pizza but burns it.",
    "A cute baby wearing sunglasses dancing in a disco.",
    "A fat orange cat fighting with a rooster in a village.",
    "A baby astronaut floating in space eating ice cream."
]

def get_story():
    """Gemini se 3 lines ki funny story mangwana"""
    topic = random.choice(TOPICS)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"Write a funny short story about '{topic}' in Hindi in exactly 3 short sentences. Split sentences with ' | '. No emojis."
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        # Cleaning text
        parts = text.split('|')
        if len(parts) < 3:
            parts = ["Ek moti billi thi.", "Wo khana paka rahi thi.", "Sab jal gaya!"]
        return parts[:3] # Sirf 3 parts lenge
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return ["Ek cute billi kitchen mein gayi.", "Usne pizza banane ki koshish ki.", "Lekin pizza jal gaya!"]

async def make_video():
    print("🚀 Viral Machine Start...")
    
    script_parts = get_story()
    print(f"📜 Story: {script_parts}")

    final_clips = []
    
    # Har sentence ke liye alag video part banayenge
    for i, line in enumerate(script_parts):
        print(f"🎥 Processing Scene {i+1}...")
        
        # 1. Audio Generate
        audio_file = f"audio_{i}.mp3"
        await Communicate(line, "hi-IN-MadhurNeural").save(audio_file)
        audio_clip = AudioFileClip(audio_file)
        
        # 2. Image Generate (High Quality 3D Disney Style)
        # Hum English keyword banayenge image ke liye
        search_key = line.split()[0] if len(line.split()) > 0 else "cat"
        # Pollinations URL with 'flux' model for better quality
        image_url = f"https://image.pollinations.ai/prompt/3d_render_pixar_style_cute_funny_{search_key}_{i}?width=1080&height=1920&model=flux&nologo=true"
        
        image_file = f"image_{i}.jpg"
        try:
            resp = requests.get(image_url, timeout=20)
            if resp.status_code == 200:
                with open(image_file, "wb") as f:
                    f.write(resp.content)
                visual_clip = ImageClip(image_file).set_duration(audio_clip.duration + 0.5)
            else:
                raise Exception("Image Failed")
        except:
            print("⚠️ Image fail, using black screen.")
            visual_clip = ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(audio_clip.duration + 0.5)

        # 3. Text Overlay
        txt_clip = TextClip(line, fontsize=50, color='yellow', stroke_color='black', stroke_width=2, font='DejaVu-Sans-Bold', size=(1000, None), method='caption')
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(visual_clip.duration)
        
        # Combine Scene
        combined = CompositeVideoClip([visual_clip, txt_clip]).set_audio(audio_clip)
        final_clips.append(combined)

    # Saare scenes ko jodna
    print("🎬 Joining Scenes...")
    final_video = concatenate_videoclips(final_clips, method="compose")
    final_video.write_videofile("viral_short.mp4", fps=24, codec="libx264", audio_codec="aac")
    print("✅ Video Ready!")

if __name__ == "__main__":
    asyncio.run(make_video())
