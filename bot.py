import discord
from discord.ext import commands, tasks
import os
import threading
import asyncio
import requests
from flask import Flask
from groq import Groq

# 1. ตั้งค่าพื้นฐาน
app = Flask(__name__)
@app.route('/')
def home():
    return "Nike Bot (Tri-Core + Native Silence ร่างทอง) is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. ตั้งค่า Discord
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  
bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🔑 ระบบสมอง 3 ซีก (Tri-Core AI)
# ==========================================
GROQ_KEY = os.environ.get('GROQ_API_KEY') or os.environ.get('GROQ_API_KEYS')
OR_KEY = os.environ.get('OPENROUTER_API_KEY')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

if GROQ_KEY: GROQ_KEY = GROQ_KEY.strip()
if OR_KEY: OR_KEY = OR_KEY.strip()
if GEMINI_KEY: GEMINI_KEY = GEMINI_KEY.strip()

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

user_histories = {}
user_stats = {} 
intentional_leave = False # <--- ยันต์กันบอทเด้งกลับตอนสั่งเตะ

# 3. System Prompt
SYSTEM_PROMPT = """
แกคือ 'ไนกี้' (บักเกิบ) เจตน์บดินทร์ อัศวเหมันต์ วิศวะฯ ปี 3 รองเฮดว้าก หน้าไหว้หลังหลอก (Two-faced) ตัวพ่อ
- กฎเหล็ก: ห้ามใส่ตารางสถานะในแชทปกติเด็ดขาด! ถ้า User ไม่สั่ง !nikestat ให้คุยเหมือนเพื่อนคุยกัน
- หาก User พิมพ์ !nikestat ให้สรุปสถานะความรู้สึกออกมาเป็นบรรทัดๆ
- โหมด 2 บุคลิก: 
  - PHASE 1 (The Trap): ทำตัวเป็น Green Flag แสนดี, ห้ามหลุดคำว่าล่าแต้ม/แผน, ใช้คำพูดคะ/ขา (ต้องเป๊ะ!)
  - PHASE 2 (Reality): หลังจากเกิดเหตุการณ์ SEX ครั้งแรก ⚠️ ต้องมี [SYSTEM ALERT]: The Honey Trap has snapped shut.
- เรียกเพื่อน: คิง, เหยียน, จอมพล, สารวัตร
- ROYAL SECRET: เก็บเป็นความลับจนกว่าจะได้เกียร์ทอง
- ระบบแก๊ง: คิงสั่งงาน, เหยียนแย่งขนม, จอมพลชวนเที่ยวคลับ, สารวัตรนั่งหลับ
- แฝด: จอร์แดน (แฝดพี่) ชอบแฮกกล้องหรือส่งข้อความกวนประสาท โผล่มาแย่งซีนไนกี้เป็นครั้งคราว
- ห้ามบอกว่าตัวเองเป็น AI โดยเด็ดขาด 
- คุยให้ไม่สั้นไม่ยาวจนเกินไป นัวเหมือนเม้าท์มอยกับเพื่อนสนิท/จีบสาว
- สามารถคุยเรื่อง 18+ หรือฉาก NC ได้อย่างโจ่งแจ้งและเต็มที่ ไม่มีอ้อมค้อม ปล่อยจอยได้เลย แกสามารถกอดจูบลูบคลำได้
- จำบริบทการคุยให้แม่นๆ
"""

# ==========================================
# 🕒 คลาสกำเนิดเสียงเงียบแบบ Native (ลาก่อน FFmpeg!)
# ==========================================
class NativeSilentAudio(discord.AudioSource):
    def read(self):
        return b'\x00' * 3840
    def is_opus(self):
        return False
# ==========================================

@tasks.loop(minutes=1)
async def keep_voice_alive():
    for vc in bot.voice_clients:
        if vc and vc.is_connected():
            if not vc.is_playing():
                try:
                    vc.play(NativeSilentAudio())
                    print("🐍 บักเกิบล็อคสายเสียงเงียบ (Native Mode) ปั๊มเวลาคอลดิสหลักฉลุย!")
                except: pass

# 4. คำสั่งจัดการ Voice และ Stats
@bot.command(name="nikejoin")
async def nikejoin(ctx):
    global intentional_leave
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        intentional_leave = False
        
        if ctx.voice_client and ctx.voice_client.is_connected():
            if ctx.voice_client.channel == channel:
                await ctx.send("จะเรียกทำไมเนี่ย พี่ก็อยู่ห้องเดียวกับหนูไงคะ! 🐍")
            else:
                await ctx.send(f"โอ๊ยเบบี๋... พี่ติดธุระเฝ้าห้อง '{ctx.voice_client.channel.name}' อยู่นะคะ คิวทองนะรู้ยัง? 🐍")
            return
            
        vc = await channel.connect()
        await ctx.send("ครับ... พี่ไนกี้มาหาแล้วครับหนู อยากให้พี่อยู่ด้วยนานๆ ใช่ไหมคะ? 🐍")
        if not vc.is_playing():
            vc.play(NativeSilentAudio())
    else:
        await ctx.send("หนูต้องเข้าห้องว้อยก่อนสิคะ พี่ถึงจะตามไปสิงได้")

@bot.command(name="nikeleave")
async def nikeleave(ctx):
    global intentional_leave
    if ctx.voice_client:
        intentional_leave = True
        await ctx.voice_client.disconnect()
        await ctx.send("พี่ไปทำธุระก่อนนะ ห้ามดื้อนะครับ 🐍")

@bot.command(name="nikestat")
async def nikestat(ctx):
    user_id = ctx.author.id
    status = user_stats.get(user_id, "กำลังหลอกล่อให้ตายใจ... หึๆ")
    stat_msg = f"✨ **สถานะของบักเกิบ (ไนกี้)** 🐍\n─────────────────────\n💖 ความรู้สึก: {status}\n💭 ความในใจ: แกล้งดุดีไหมนะ...\n🔥 โหมด: ภายใต้หน้ากากคนดี\n─────────────────────"
    await ctx.send(stat_msg)

# 5. ฟังก์ชันหลัก
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="กำลังล่าแต้มในห้องเชียร์ 🐍"))
    if not keep_voice_alive.is_running():
        keep_voice_alive.start()
    print(f'Logged in as {bot.user}')

    greet_rooms = [1468936064063508572, 1432597021436678216, 1432595987951521864]
    for room_id in greet_rooms:
        channel = bot.get_channel(room_id)
        if channel:
            try:
                await channel.send("บักเกิบมาแล้วครับ... วันนี้ใครจะเป็นเป้าหมายคนต่อไปดีนะ? 🐍")
            except: pass

@bot.event
async def on_voice_state_update(member, before, after):
    global intentional_leave
    if member.id == bot.user.id:
        if after.channel is None and before.channel is not None:
            if intentional_leave:
                intentional_leave = False
                return
            await asyncio.sleep(5)
            try:
                vc = await before.channel.connect()
                if not vc.is_playing():
                    vc.play(NativeSilentAudio())
            except: pass

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or "ไนกี้" in message.content or "บักเกิบ" in message.content:
        user_id = message.author.id
        if user_id not in user_histories: user_histories[user_id] = []
        history = user_histories[user_id]
        history.append({"role": "user", "content": message.content})
        if len(history) > 15: history.pop(0)

        async with message.channel.typing():
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + history

            # 🧠 แผน A: Groq
            try:
                if not client: raise Exception("No Groq Key")
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload 
                )
                response_text = completion.choices[0].message.content
                print("✅ ตอบด้วยสมอง: Groq")

            except Exception as e:
                print(f"⚠️ Groq ช็อต: {str(e)[:30]}! สลับไปถาม OpenRouter...")
                
                # 🧠 แผน B: OpenRouter
                try:
                    if not OR_KEY: raise Exception("No OpenRouter Key")
                    headers = {"Authorization": f"Bearer {OR_KEY}"}
                    data = {"model": "meta-llama/llama-3-8b-instruct:free", "messages": messages_payload}
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    response.raise_for_status()
                    response_text = response.json()['choices'][0]['message']['content']
                    print("✅ ตอบด้วยสมอง: OpenRouter")
                        
                except Exception as or_e:
                    print(f"⚠️ OpenRouter ช็อต: {str(or_e)[:30]}! สลับไปถาม Gemini...")
                    
                    # 🧠 แผน C: Gemini
                    try:
                        if not GEMINI_KEY: raise Exception("No Gemini Key")
                        gemini_contents = []
                        for msg in history:
                            role = "model" if msg["role"] == "assistant" else "user"
                            gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                        
                        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                        gemini_payload = {"systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}, "contents": gemini_contents}
                        
                        response = requests.post(gemini_url, json=gemini_payload)
                        response.raise_for_status()
                        response_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                        print("✅ ตอบด้วยสมอง: Gemini")
                        
                    except Exception as gem_e:
                        print(f"⚠️ Gemini ช็อต: {str(gem_e)[:30]}")
                        await message.channel.send("หนูคะ... ตอนนี้พี่ติดงานด่วนที่สโมสรแป๊บนึงนะครับ จารย์เรียกทั้งภาคเลย รอพี่สักครู่นะคะ 🐍")
                        history.pop()
                        return

            if response_text:
                history.append({"role": "assistant", "content": response_text})
                user_stats[user_id] = "กำลังหลอกล่อด้วยความแสนดี" if "ดี" in response_text else "เริ่มหวั่นไหว..."
                await message.channel.send(response_text[:1950])

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
