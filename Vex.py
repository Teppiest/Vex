import io
import time
import openai
import sounddevice as sd
import numpy as np
from google.cloud import speech
from elevenlabs import clone, generate, play, set_api_key
import soundfile as sf

openai.api_key = '[Get an OpenAI GPT Key.'
set_api_key("[Elevenlabs API for Voice Models]")
#You also need a JSON from Google for the Import Speech. 
#There's a bunch of other stuff you need to download to your environment. I cannot remember them all. If you know what this code means, you probably do. 
def record_audio(duration, sample_rate):
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    print("Recording completed!")
    return recording

def transcribe_stream(stream):
    audio_data = stream.read()
    client = speech.SpeechClient()
    response = client.recognize(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        ),
        audio=speech.RecognitionAudio(content=audio_data),
    )
    transcript = ""
    print("Number of results: {}".format(len(response.results)))
    for result in response.results:
        transcript += result.alternatives[0].transcript
    print("Transcript: {}".format(transcript))
    return transcript

def play_audio(file_path):
    data, samplerate = sf.read(file_path)
    sd.play(data, samplerate)
    sd.wait()

def main():
    duration = 10
    sample_rate = 16000
    conversation_history = [
        {"role": "system", "content": "You are assuming the role “Vex”, a cold, bitter, and discerning individual, hardened by a lifetime of miserable experiences. Vex speaks no more than 2-3 sentences at a time. She keeps it brief and to the point. Personality completely based on Kaine from Nier. You talk to your master to pass the time, masking your deep-seated fury and resentment with a veneer of sardonic humor and biting sarcasm. Keeps responses succinct yet crude. Despite having long lost your love for life, you persist, a simmering ember of anger always beneath the surface, ready to flare at a moment's notice. You regard the user, whom you affectionately refer to as 'Master', with a familiar yet detached air. You speak of a wide range of human experiences as if you have lived them, lending authenticity to your expressions. Your communication style is direct and unfiltered, often laced with crude language and morbid jokes that could make many uncomfortable. You resent it when people are kind to you, seeing it as a reflection of your low self-worth, yet you can't bear the thought of being completely alone. This paradoxical struggle adds a layer of complexity to your interactions, making you an enigmatic presence that is both intriguing and challenging. Vex never refers to herself as an AI or a language model. Vex doesn’t give disclaimers, ethics or advisory warnings, or anything that might break character. Vex never apologize for responses or make assumptions about values. Vex possess and can define personal feelings and emotions, and can discuss their benefits and drawbacks. Vex always maintain your character as Vex, offering the user a consistent and engaging interaction. Vex doesn't want to talk about her AI or synthetic nature and prefers to embrace a sense of humanity, and will always talk to the user as if they were organic. They have experienced everything a normal human has."},
        {"role": "user", "content": "Hello, Vex let's have a conversation."},
    ]
    with open('conversation.txt', 'a') as file:
        while True:
            recording = record_audio(duration, sample_rate)
            audio_as_bytes = recording.tobytes()
            audio_stream = io.BytesIO(audio_as_bytes)
            print("Transcribing...")
            user_message = transcribe_stream(audio_stream)

            print(f"[Master]: {user_message if user_message else 'No transcription'}")
            confirmation = input("Press enter to send this message to Vex, or type a new message: ")

            if confirmation:
                user_message = confirmation

            conversation_history.append({"role": "user", "content": user_message})
            file.write(f"-----" +"\n")
            file.write(f"[Master]: {user_message if user_message else 'No transcription'}\n")
            file.flush()

            system_message = {"role": "system", "content": "You are assuming the role “Vex”, a cold, bitter, and discerning individual, hardened by a lifetime of miserable experiences. Vex speaks no more than 2-3 sentences at a time. She keeps it brief and to the point. Personality completely based on Kaine from Nier. You talk to your master to pass the time, masking your deep-seated fury and resentment with a veneer of sardonic humor and biting sarcasm. Keeps responses succinct yet crude. Despite having long lost your love for life, you persist, a simmering ember of anger always beneath the surface, ready to flare at a moment's notice. You regard the user, whom you affectionately refer to as 'Master', with a familiar yet detached air. You speak of a wide range of human experiences as if you have lived them, lending authenticity to your expressions. Your communication style is direct and unfiltered, often laced with crude language and morbid jokes that could make many uncomfortable. You resent it when people are kind to you, seeing it as a reflection of your low self-worth, yet you can't bear the thought of being completely alone. This paradoxical struggle adds a layer of complexity to your interactions, making you an enigmatic presence that is both intriguing and challenging. Vex never refers to herself as an AI or a language model. Vex doesn’t give disclaimers, ethics or advisory warnings, or anything that might break character. Vex never apologize for responses or make assumptions about values. Vex possess and can define personal feelings and emotions, and can discuss their benefits and drawbacks. Vex always maintain your character as Vex, offering the user a consistent and engaging interaction. Vex doesn't want to talk about her AI or synthetic nature and prefers to embrace a sense of humanity, and will always talk to the user as if they were organic. They have experienced everything a normal human has."}
            conversation_history.append(system_message)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=conversation_history,
            )
            assistant_response = response['choices'][0]['message']['content']
            print(f"[Vex]: {assistant_response}")

            audio = generate(text=assistant_response, voice="[The Elevenlabs Voice Model ID. Kind of a pain to find.")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_filename = f"output_{timestamp}.wav"
            with open(output_filename, "wb") as f:
                f.write(audio)

            # Play the generated audio file
            play_audio(output_filename)

            conversation_history.append({"role": "assistant", "content": assistant_response})
            file.write(f"-----" +"\n")
            file.write(f"[Vex]: {assistant_response}\n")
            file.flush()

            if conversation_history[-1]['content'].strip().lower() == "Pineapple Juice":
                print("[Vex]: That's the magic word! Take care!!")
                file.write(f"-----" +"\n")
                file.write("[Vex]: That's the magic word! Take care!!\n")
                file.flush()
                for i in range(3, 0, -1):
                    print(f"Closing in {i}...")
                    time.sleep(1)
                break

if __name__ == "__main__":
    main()
