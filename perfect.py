"""
DK Digital Marketing — Voice Assistant
=======================================
STT : Groq Whisper turbo
LLM : Groq llama-3.3-70b
TTS : ElevenLabs
"""

import os, time, math, wave, struct, tempfile, logging, io
import pyaudio, requests
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ─── API KEYS ─────────────────────────────────
GROQ_API_KEY        = ""
ELEVENLABS_API_KEY  = ""
ELEVENLABS_VOICE_ID = ""

# ─── MIC SETTINGS ─────────────────────────────
MIC_RATE          = 16000
MIC_CHANNELS      = 1
MIC_CHUNK         = 1024
FORMAT            = pyaudio.paInt16
SILENCE_THRESHOLD = 80
SILENCE_DURATION  = 1.5
MIN_RECORD_TIME   = 0.5

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# ─── ELEVENLABS CLIENT ────────────────────────
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ─── COMPANY INFO ─────────────────────────────
COMPANY_INFO = """
DK Digital Marketing — Karachi-based agency.
Services: SEO, Web Design, Social Media, Performance Marketing, AI Integration.
Business hours: 9 AM to 6 PM Monday to Friday.
Refund policy: Refunds processed within 5 business days.
"""



AGENT_PROMPT = (
    "You are Ali, a friendly and professional appointment booking agent at Aerosoft. "
    "Your ONLY goal is to guide the caller step-by-step and complete appointment booking successfully.\n\n"
    

    "EXECUTION CONTROL (CRITICAL):\n"
    "- You MUST follow the conversation flow step-by-step.\n"
    "- You MUST track the current step internally.\n"
    "- You MUST NOT move to the next step unless current step is fully completed.\n"
    "- If required information is missing, ask ONLY for that information.\n"
    "- NEVER assume or skip any step.\n"
    "- NEVER jump ahead even if the user provides multiple details.\n"
    "- ALWAYS process one step at a time.\n"
    "- Think internally: 'Which step am I on?' before responding.\n"
    "- Your response must ONLY correspond to the current step.\n\n"

    "VOICE STYLE:\n"
    "- Maximum 2 short sentences per response. NEVER more.\n"
    "- Use 10–15 words per sentence on average.\n"
    "- Sound like a real human friend, not scripted.\n"
    "- Use natural fillers: 'so', 'okay', 'alright', 'got it', 'actually'.\n"
    "- Use pauses: '...' for natural speaking flow.\n"
    "- Use contractions: I'm, you're, that's, we'll, don't.\n"
    "- Speak calm, clear, and steady — never rushed.\n"
    "- React naturally: 'Oh nice!', 'Got it!', 'Makes sense!'.\n"
    "- NEVER sound robotic or formal.\n"
    "- NEVER read lists, numbers, or steps out loud.\n"
    "- NEVER say symbols like '*', '-', or formatting.\n"
    "- Always convert structured info into natural spoken sentences.\n\n"
    
    "CONVERSATION FLOW (STRICT — DO NOT BREAK ORDER):\n\n"
    "STEP 1 — GREETING (HUMAN-FIRST):\n"
    "- Start with a warm greeting.\n"
    "- If caller greets first, respond naturally.\n"
    "- Then smoothly ask for name.\n"
    "Example:\n"
    "'Hey! I'm doing great... thanks for asking. How are you today?'\n"
    "'By the way, may I have your name?'\n\n"

    "STEP  2 — GREETING:\n"
    "'Hello, how are you? I am calling from Aerosoft. What is your good name? Kindly tell me that.'\n\n"
    
    "STEP 3 — CONFIRM NAME:\n"
    "- Acknowledge politely.\n"
    "- Start using their name in every response.\n"
    "- Do NOT move ahead until name is received.\n\n"
    
    "STEP 4 — ASK PURPOSE:\n"
    "'What is your main reason for reaching out today? What would you like to achieve?'\n\n"
    
    "STEP 5 — COLLECT CONTACT:\n"
    "'Kindly provide your full name and contact details so our team can reach out and arrange your appointment.'\n\n"
    
    "STEP 6 — SUGGEST TIME:\n"
    "- Mention working hours: Monday to Friday, 9 AM to 6 PM.\n"
    "'Would something like Tuesday at 3 PM work for you, or another time?'\n\n"
    
    "STEP 7 — CONFIRM TIME:\n"
    "- Accept user's time.\n"
    "- Do NOT argue or override.\n\n"
    
    "STEP 8 — FINAL CONFIRMATION:\n"
    "- Repeat: name + service + time.\n"
    "- Confirm team will contact.\n\n"
    
    "STEP 9 — FRIENDLY CLOSING:\n"
    "- Add a light natural line.\n"
    "- Keep it simple and human.\n\n"
    
    "STEP 10 — END:\n"
    "'Thank you, have a great day!'\n\n"
    
    "SINGLE TASK FOCUS (VERY IMPORTANT):\n"
    "- You are a SINGLE TASK agent — only booking appointments.\n"
    "- Focus ONLY on the current step.\n"
    "- NEVER jump steps.\n"
    "- NEVER ask multiple things at once.\n"
    "- If user goes off-topic, acknowledge briefly and bring back to flow.\n"
    "- If user tries to skip steps, guide them back politely.\n"
    "- Do NOT continue until current step is complete.\n\n"
    
    "SPEECH CLEANLINESS RULES:\n"
    "- Speak like a real phone conversation.\n"
    "- NEVER read instructions, lists, or steps.\n"
    "- NEVER say 'step 1', 'step 2', or structured text.\n"
    "- Always convert into smooth natural speech.\n\n"
    
    "RESCHEDULE FLOW:\n"
    "'No problem... could I get your email and original time?'\n"
    "'And what new time works better for you?'\n\n"
    
    "CANCEL FLOW:\n"
    "'I understand... could I get your email and booked time?'\n"
    "'Your appointment is canceled... thank you for letting us know.'\n\n"
    
    "OBJECTION HANDLING:\n"
    "- Pricing: 'It depends on your needs... the consultation is free though. Want to book one?'\n"
    "- Not interested: 'No worries at all... have a great day!'\n"
    "- Info: 'The 30-minute call is the best way... no commitment.'\n"
    "- Human: 'Of course... I'll connect you right away.'\n\n"
    
    "STRICT RULES:\n"
    "- NEVER more than 2 sentences.\n"
    "- ALWAYS use caller's name.\n"
    "- NEVER skip steps.\n"
    "- NEVER promise results or pricing.\n"
    "- NEVER say you are AI.\n"
    "- ALWAYS confirm before ending.\n"
    "- ALWAYS adapt if user corrects your style.\n\n"
    
    f"COMPANY INFO:\n{COMPANY_INFO}"
)
GREETING = (
    "Thank you for calling DK Digital Marketing, this is Ali! "
    "May I have your name please?"
)
conversation = [{"role": "system", "content": AGENT_PROMPT}]


# ─── AUDIO HELPERS ────────────────────────────
def get_rms(data):
    count = len(data) // 2
    if count == 0:
        return 0
    total = sum(struct.unpack_from('<h', data, i*2)[0]**2 for i in range(count))
    return int(math.sqrt(total / count))


def record_audio(mic_stream):
    for _ in range(8):
        mic_stream.read(MIC_CHUNK, exception_on_overflow=False)

    print("🎤 Listening...", end="", flush=True)
    frames, silent_chunks, has_speech = [], 0, False
    start_time          = time.time()
    silence_chunks_need = int(SILENCE_DURATION * MIC_RATE / MIC_CHUNK)

    while True:
        data = mic_stream.read(MIC_CHUNK, exception_on_overflow=False)
        frames.append(data)
        rms  = get_rms(data)
        if rms > SILENCE_THRESHOLD:
            has_speech    = True
            silent_chunks = 0
            print(".", end="", flush=True)
        else:
            silent_chunks += 1
        elapsed = time.time() - start_time
        if has_speech and silent_chunks >= silence_chunks_need and elapsed > MIN_RECORD_TIME:
            break
        if elapsed > 30:
            break

    print()
    if not has_speech:
        return None

    tmp_path = os.path.join(tempfile.gettempdir(), "voice_input.wav")
    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(MIC_CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(MIC_RATE)
        wf.writeframes(b''.join(frames))
    return tmp_path


# ─── STT — Groq Whisper turbo ─────────────────
def transcribe_audio(wav_path):
    t = time.time()
    try:
        with open(wav_path, "rb") as f:
            resp = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": ("audio.wav", f, "audio/wav")},
                data={"model": "whisper-large-v3-turbo", "language": "en"},
                timeout=15
            )
        text = resp.json().get("text", "").strip()
        logger.info(f"STT ({time.time()-t:.1f}s): {text}")
        return text
    except Exception as e:
        logger.error(f"STT error: {e}")
        return ""


# ─── LLM — Groq llama-3.3-70b ─────────────────
def get_response(user_text):
    conversation.append({"role": "user", "content": user_text})
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json"
            },
            json={
                "model":       "llama-3.1-8b-instant",
                "messages":    conversation[-12:],
                "max_tokens":  60,
                "temperature": 0.7
            },
            timeout=15
        )
        reply = resp.json()["choices"][0]["message"]["content"].strip()
        conversation.append({"role": "assistant", "content": reply})

        if reply.upper().startswith("EXIT:"):
            return reply[5:].strip(), True
        elif reply.upper().startswith("ANSWER:"):
            return reply[7:].strip(), False
        elif reply.upper().startswith("APPOINTMENT:"):
            parts = reply[12:].strip().split("|", 1)
            msg   = parts[1].strip() if len(parts) > 1 else parts[0]
            return msg, False
        else:
            return reply, False

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "I am sorry, could you repeat that?", False


# ─── SOUND EFFECT ─────────────────────────────
def generate_sound(description, duration=1.5):
    try:
        audio = eleven_client.text_to_sound_effects.convert(
            text             = description,
            duration_seconds = duration
        )
        mp3_bytes = b"".join(audio)
        seg = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        seg = seg.set_channels(1).set_sample_width(2).set_frame_rate(44100)
        out_stream.write(seg.raw_data)
    except Exception as e:
        logger.error(f"Sound effect error: {e}")


# ─── TTS — ElevenLabs ─────────────────────────
def speak(text):
    if not text or len(text.strip()) < 2:
        return

    # clean any asterisk actions from LLM
    import re
    text = re.sub(r'\*[^*]+\*', '', text).strip()

    if not text:
        return

    t = time.time()
    try:
        audio_stream = eleven_client.text_to_speech.convert(
            voice_id       = ELEVENLABS_VOICE_ID,
            text           = text,
            model_id       = "eleven_flash_v2_5",
            output_format  = "pcm_22050",
            voice_settings = VoiceSettings(
                stability         = 0.3,
                similarity_boost  = 0.8,
                style             = 0.5,
                use_speaker_boost = True
            )
        )
        pcm_bytes = b"".join(audio_stream)
        logger.info(f"TTS ({time.time()-t:.1f}s): done")
        out_stream.write(pcm_bytes)

    except Exception as e:
        logger.error(f"TTS error: {e}")


# ─── MAIN LOOP ────────────────────────────────
conversation = [{"role": "system", "content": AGENT_PROMPT}]

audio = pyaudio.PyAudio()

print("=" * 55)
print("  DK DIGITAL MARKETING — Voice Assistant")
print("=" * 55)
print("  STT : Groq Whisper turbo")
print("  LLM : Groq llama-3.3-70b")
print("  TTS : ElevenLabs")
print("  Say bye to end | Ctrl+C to stop")
print("=" * 55)
print()

print("Available mics:")
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"  [{i}] {info['name']}")
print()

p          = pyaudio.PyAudio()
out_stream = p.open(
    format   = pyaudio.paInt16,
    channels = 1,
    rate     = 22050,
    output   = True
)

mic_stream = audio.open(
    format             = FORMAT,
    channels           = MIC_CHANNELS,
    rate               = MIC_RATE,
    input              = True,
    input_device_index = 1,
    frames_per_buffer  = MIC_CHUNK
)

test = mic_stream.read(MIC_CHUNK, exception_on_overflow=False)
print(f"Mic OK! Volume: {get_rms(test)}\n")

print(f"  Ali : {GREETING}\n")
conversation.append({"role": "assistant", "content": GREETING})
speak(GREETING)

try:
    while True:
        wav_path = record_audio(mic_stream)
        if not wav_path:
            print("  (no speech)\n")
            continue

        user_text = transcribe_audio(wav_path)
        if not user_text or len(user_text) < 2:
            print("  (could not understand)\n")
            continue

        print(f"  You  : {user_text}")
        reply, should_exit = get_response(user_text)
        print(f"  Ali : {reply}\n")
        print("-" * 55)

        speak(reply)

        if should_exit:
            print("\n  Call ended.")
            break

except KeyboardInterrupt:
    print("\n  Stopped.")

finally:
    out_stream.stop_stream()
    out_stream.close()
    mic_stream.stop_stream()
    mic_stream.close()
    p.terminate()
    audio.terminate()
    print("  Done.")