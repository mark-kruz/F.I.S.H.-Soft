from openai import OpenAI
import pyaudio
from pathlib import Path
import wave
import keyboard

client = OpenAI(api_key="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")
chunk = 1024
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 5

soundfile = 'test.wav'

p = pyaudio.PyAudio()

print("ready, enter Y to make a new recording")
if input() == "Y":

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')
    # Save the recorded data as a WAV file
    wf = wave.open(soundfile, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

sound = open('test.wav', "rb")
transcript = client.audio.transcriptions.create(model="whisper-1", file=sound)
text = transcript.text
cleaned_text = client.chat.completions.create(
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "system", "content": "You are a system, which fixes transcripts generated by speech-to-text. You should correct individual letters in words or entire words. Your response should be only the repaired text."},
    {"role": "user", "content": text},
  ]
)
print(text)
print(cleaned_text.choices[0].message.content)
response = client.chat.completions.create(
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "system", "content": "You are a digital assistant that is a mounted fish on the wall. You answer factually, but slightly comedicly and witty."},
    {"role": "user", "content": text},
  ]
)
speech_file_path = Path(__file__).parent / "speech.mp3"
response_audio = client.audio.speech.create(
  model="tts-1-hd",
  voice="onyx",
  input=response.choices[0].message.content
)
response_audio.stream_to_file(speech_file_path)