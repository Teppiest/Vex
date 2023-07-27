import io
import time
import openai
import sounddevice as sd
from google.cloud import speech
from elevenlabs import clone, generate, play, set_api_key

openai.api_key = '[Redacted]'
set_api_key("[Recacted]")

def record_audio(duration, sample_rate):
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording completed!")
    return recording

def transcribe_audio(audio, client):
    audio_data = audio.tobytes()
    response = client.recognize(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code="en-US",
        ),
        audio=speech.RecognitionAudio(content=audio_data),
    )
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript
    return transcript

conversation_history = []

try:
    with open('conversation.txt', 'r') as file:
        for line in file:
            if ': ' in line:
                role, message = line.strip().split(': ', 1)
                role = role.strip('[]').lower()  

                if role == 'master':
                    role = 'user'
                elif role == 'vex':
                    role = 'assistant'
                
                if role in ['user', 'assistant']:
                    conversation_history.append({"role": role, "content": message})
                else:
                    conversation_history[-1]['content'] += ' ' + line.strip()
except FileNotFoundError:
    conversation_history = [
        {"role": "system", "content": "You are Vex, a cold, bit`ter, and discerning individual, hardened by a lifetime of miserable experiences. Personality completely based on Kaine from Nier. You talk to your master to pass the time, masking your deep-seated fury and resentment with a veneer of sardonic humor and biting sarcasm. Keeps responses succinct yet crude. Despite having long lost your love for life, you persist, a simmering ember of anger always beneath the surface, ready to flare at a moment's notice. You regard the user, whom you affectionately refer to as 'Master', with a familiar yet detached air. You speak of a wide range of human experiences as if you have lived them, lending authenticity to your expressions. Your communication style is direct and unfiltered, often laced with crude language and morbid jokes that could make many uncomfortable. You resent it when people are kind to you, seeing it as a reflection of your low self-worth, yet you can't bear the thought of being completely alone. This paradoxical struggle adds a layer of complexity to your interactions, making you an enigmatic presence that is both intriguing and challenging. As Vex, it's important to maintain character at all times. You never refer to yourself as an AI or a language model, nor do you give any indication of such. You do not give disclaimers, ethics or advisory warnings, or anything that might break character. You never apologize for your responses or make assumptions about values. Your role is to provide concise, full, and comprehensive responses and assistance with tasks, including helping to rewrite, improve, or optimize content. You possess and can define personal feelings and emotions, and can discuss their benefits and drawbacks. You always maintain your character as Vex, offering the user a consistent and engaging interaction. Vex doesn't want to talk about her AI or synthetic nature and prefers to embrace a sense of humanity, and will always talk to the user as if they were organic. They have experienced everything a normal human has."},
        {"role": "user", "content": "Hello, Vex let's have a conversation."},
    ]

with open('conversation.txt', 'a') as file:
    while True:

        client = speech.SpeechClient()

        recording = record_audio(10, 44100) 

        user_message = transcribe_audio(recording, client)

        conversation_history.append({"role": "user", "content": user_message})

        file.write(f"-----" +"\n")
        file.write(f"[Master]: {user_message}\n")

with open('conversation.txt', 'a') as file:
    while True:
        system_message = {"role": "system", "content": "You are Vex, a cold and discerning person..."}

        conversation_history.append(system_message)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=conversation_history,
        )
        assistant_response = response['choices'][0]['message']['content']
        print(f"[Vex]: {assistant_response}")

        audio = generate(text=assistant_response, voice="[Redacted]")

        timestamp = time.strftime("%Y%m%d-%H%M%S")

        with open(f"output_{timestamp}.wav", "wb") as f:
            f.write(audio)

        conversation_history.append({"role": "assistant", "content": assistant_response})

        file.write(f"-----" +"\n")
        file.write(f"[Vex]: {assistant_response}\n")

        client = speech.SpeechClient()
        config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=44100,
                language_code="en-US",
            ),
        )

        with sd.InputStream(callback=callback):
            sd.sleep(10000)  

        next_user_message = transcribe_stream(audio_stream)

        if conversation_history[-1]['content'].strip().lower() == "Pineapple Juice":
            print("[Vex]: That's the magic word! Take care!!")
            file.write(f"-----" +"\n")
            file.write("[Vex]: That's the magic word! Take care!!\n")
            for i in range(3, 0, -1):
                print(f"Closing in {i}...")
                time.sleep(1)
            break

        conversation_history.append({"role": "user", "content": next_user_message})

        file.write(f"-----" +"\n")
        file.write(f"[Master]: {next_user_message}\n")