# Voice_agent
STT to TTS


 Features

🎤 Real-time Speech-to-Text — Groq Whisper turbo for fast, accurate transcription
🧠 Intelligent Conversation — Groq LLaMA 3.3-70b for natural human-like responses
🔊 Text-to-Speech — ElevenLabs for realistic voice output
📅 Appointment Booking Flow — Strict step-by-step booking conversation
🔇 Silence Detection — Automatically detects when user stops speaking
🔁 Reschedule & Cancel — Handles changes to existing appointments
🛡️ Objection Handling — Manages pricing, interest, and off-topic responses

🛠️ Tech Stack
ComponentTechnologySpeech-to-TextGroq Whisper Large v3 TurboLanguage ModelGroq LLaMA 3.1-8b / 3.3-70bText-to-SpeechElevenLabs Flash v2.5Audio I/OPyAudioAudio Processingpydub


 Installation
Step 1 — Clone the repository
bashgit clone https://github.com/your-username/dk-voice-assistant.git
cd dk-voice-assistant
Step 2 — Install dependencies
bashpip install pyaudio requests pydub elevenlabs
Step 3 — Configure API keys
Open main.py and update these values:
pythonGROQ_API_KEY        = "your_groq_api_key"
ELEVENLABS_API_KEY  = "your_elevenlabs_api_key"
ELEVENLABS_VOICE_ID = "your_voice_id"
Step 4 — Run the assistant
bashpython main.py


Step 1 → Greeting
Step 2 → Ask caller's name
Step 3 → Confirm name
Step 4 → Ask purpose of call
Step 5 → Collect contact details
Step 6 → Suggest appointment time
Step 7 → Confirm time with caller
Step 8 → Final confirmation
Step 9 → Friendly closing
Step 10 → End call

🎛️ Configuration
SettingDefaultDescriptionMIC_RATE16000Microphone sample rateSILENCE_THRESHOLD80Volume level to detect silenceSILENCE_DURATION1.5sSeconds of silence before stoppingMIN_RECORD_TIME0.5sMinimum recording time
