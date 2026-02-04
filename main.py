import os, asyncio, requests
import google.generativeai as genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# API Setup
API_KEY = os.getenv("GEMINI_API_KEY")

async def start_engine():
    try:
        print("📝 Step 1: Trending Topic & Script...")
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Trend finding prompt
        prompt = "Write 2 viral mind-blowing facts about Space in Hindi. Keep it very short and engaging."
        res = model.generate_content(prompt)
        facts = [f.strip() for f in res.text.split('\n') if len(f) > 5][:2]
        
        print("🎙️ Step 2: Making Voice & Video...")
        full_text = " . ".join(facts)
        await Communicate(full_text, "hi-IN-MadhurNeural").save("v.mp3")
        audio = AudioFileClip("v.mp3")
        
        clips = []
        dur = audio.duration / len(facts)
        for i, t in enumerate(facts):
            url = f"https://pollinations.ai/p/{t.replace(' ','_')}?width=1080&height=1920&seed={i}"
            with open(f"{i}.jpg", "wb") as f: f.write(requests.get(url).content)
            clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))
        
        # FILE NAME KO "viral_short.mp4" HI RAKHNA HAI
        final_video_name = "viral_short.mp4"
        concatenate_videoclips(clips, method="compose").set_audio(audio).write_videofile(final_video_name, fps=24, codec="libx264")
        
        print(f"✅ SUCCESS! Video saved as {final_video_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(start_engine())
