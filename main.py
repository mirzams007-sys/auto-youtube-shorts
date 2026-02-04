import os, asyncio, requests, json
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# API Setup
API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_script():
    """Direct API call - No Google library needed"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": "Write 2 short viral space facts in Hindi. Just facts, no intro."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        # AI se text nikalna
        text = data['candidates'][0]['content']['parts'][0]['text']
        return text
    except Exception as e:
        print(f"⚠️ AI API Error: {e}")
        return "Antariksh bilkul shant hai. Fact 1: Antariksh mein koi awaz nahi hoti. Fact 2: Suraj ke andar 10 lakh prithvi sama sakti hain."

async def start_machine():
    try:
        print("📝 Step 1: Getting Script (Direct Method)...")
        script = get_ai_script()
        facts = [f.strip() for f in script.split('\n') if len(f) > 5][:2]
        print(f"✅ Script Ready!")

        print("🎙️ Step 2: Generating Voice...")
        full_text = " . ".join(facts)
        await Communicate(full_text, "hi-IN-MadhurNeural").save("v.mp3")
        audio = AudioFileClip("v.mp3")

        print("🖼️ Step 3: Generating Images...")
        clips = []
        dur = audio.duration / len(facts)
        for i, t in enumerate(facts):
            # Clean text for URL
            clean_t = "".join(e for e in t if e.isalnum() or e.isspace())
            url = f"https://pollinations.ai/p/{clean_t.replace(' ','_')}?width=1080&height=1920&seed={i}"
            img_data = requests.get(url).content
            with open(f"{i}.jpg", "wb") as f: f.write(img_data)
            clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))

        print("🎬 Step 4: Finalizing Video...")
        final_video = "viral_short.mp4"
        clip = concatenate_videoclips(clips, method="compose").set_audio(audio)
        clip.write_videofile(final_video, fps=24, codec="libx264", audio_codec="aac")
        print("✅ ALL DONE!")
        
    except Exception as e:
        print(f"❌ Final Error: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(start_machine())
