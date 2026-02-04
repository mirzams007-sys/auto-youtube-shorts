import os, asyncio, requests
from google import genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# 1. Naya AI Setup
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

async def start_engine():
    try:
        print("📝 Step 1: Writing Script with New AI Engine...")
        
        # Viral topic script mangna
        prompt = "Write 2 viral mind-blowing facts about Space in Hindi. Keep it very short and engaging. Give facts only."
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )
        
        facts_text = response.text
        facts = [f.strip() for f in facts_text.split('\n') if len(f) > 5][:2]
        
        print(f"🎙️ Step 2: Making Voice for: {facts[0]}")
        full_text = " . ".join(facts)
        await Communicate(full_text, "hi-IN-MadhurNeural").save("v.mp3")
        audio = AudioFileClip("v.mp3")
        
        print("🖼️ Step 3: Making Images...")
        clips = []
        dur = audio.duration / len(facts)
        for i, t in enumerate(facts):
            # Image generation
            url = f"https://pollinations.ai/p/{t.replace(' ','_')}?width=1080&height=1920&seed={i}"
            img_data = requests.get(url).content
            with open(f"{i}.jpg", "wb") as f: f.write(img_data)
            clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))
        
        print("🎬 Step 4: Finalizing Video...")
        final_video_name = "viral_short.mp4"
        final_clip = concatenate_videoclips(clips, method="compose").set_audio(audio)
        final_clip.write_videofile(final_video_name, fps=24, codec="libx264", audio_codec="aac")
        
        print("✅ SUCCESS! Everything is perfect.")
        
    except Exception as e:
        print(f"❌ New Error: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(start_engine())
