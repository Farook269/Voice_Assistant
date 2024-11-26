import pyaudio
import wave
import numpy as np

def record_audio(filename="temp_audio.wav", duration=5, sample_rate=44100, channels=1, chunk=1024, return_data=False):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print(f"Recording for {duration} seconds...")

    frames = []

    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Audio saved as {filename}")

    if return_data:
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        return audio_data, sample_rate
    else:
        return filename