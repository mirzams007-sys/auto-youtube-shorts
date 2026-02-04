python
import os, asyncio, requests
import google.generativeai as genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# 1. AI Setup
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def make_viral_video():
    print("🌐 Finding trending topics...")
    # Machine khud dhoondegi ke aaj kal kya trend chal raha hai
    prompt = "Identify a trending viral topic for YouTube Shorts right now (e.g., Space, AI, Life Hacks, or Mystery). Write a 30-second script in Hindi about it. Give 3 mind-blowing facts. Format: Fact 1, Fact 2, Fact 3. No extra text."
    res = model.generate_content(prompt)
    facts = [f.strip() for f in res.text.split('\n') if len(f) > 5][:3]
    
    print(f"🎙️ Topic found! Creating voiceover...")
    full_script = " . ".join(facts)
    await Communicate(full_script, "hi-IN-MadhurNeural").save("voice.mp3")
    audio = AudioFileClip("voice.mp3")

    print("🖼️ Generating AI Images for each fact...")
    clips = []
    dur = audio.duration / len(facts)
    for i, t in enumerate(facts):
        # AI se HD 9:16 (Shorts size) image lena
        img_url = f"https://pollinations.ai/p/{t.replace(' ','_')}?width=1080&height=1920&seed={i}"
        with open(f"{i}.jpg", "wb") as f: f.write(requests.get(img_url).content)
        clips.append(ImageClip(f"{i}.jpg").set_duration(dur).set_fps(24))

    print("🎬 Assembling Final Video...")
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile("viral_short.mp4", fps=24, codec="libx264")
    print("✅ Machine Task Completed!")

if __name__ == "__main__":
    asyncio.run(make_viral_video())
