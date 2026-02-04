import os, asyncio, requests
import google.generativeai as genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# API Setup
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

async def start_engine():
    try:
        print("📝 Step 1: Writing Script...")
        
        # Sabse behtar model dhoondna (Flash ya Pro)
        model_name = 'gemini-1.5-flash'
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Write 2 short interesting facts about Space in Hindi.")
        except:
            print("⚠️ Flash not found, trying alternative...")
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Write 2 short interesting facts about Space in Hindi.")

        facts = [f.strip() for f in response.text.split('\n') if len(f) > 5][:2]
        print(f"✅ Script ready: {facts[0][:20]}...")

        print("🎙️ Step 2: Making Voiceover...")
        full_text = " . ".join(facts)
        await Communicate(full_text, "hi-IN-MadhurNeural").save("v.mp3")
        audio = AudioFileClip("v.mp3")
        
        print("🖼️ Step 3: Generating Images...")
        clips = []
        dur = audio.duration / len(facts)
        for i, t in enumerate(facts):
            url = f"https://pollinations.ai/p/{t.replace(' ','_')}?width=1080&height=1920&seed={i}"
            with open(f"{i}.jpg", "wb") as f: f.write(requests.get(url).content)
            clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))
        
        print("🎬 Step 4: Finalizing Video...")
        final_video_name = "viral_short.mp4"
        final_clip = concatenate_videoclips(clips, method="compose").set_audio(audio)
        final_clip.write_videofile(final_video_name, fps=24, codec="libx264")
        
        print("✅ SUCCESS! Video is ready.")
        
    except Exception as e:
        print(f"❌ Error Details: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(start_engine())
