import os
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

# Set the API key
os.environ['DG_API_KEY'] = "fc56f9e7cc7adc88c6cbdbec83883043da3b66e3"

def transcribe_audio(file_path):
    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key=os.getenv("DG_API_KEY"))

        # Read the audio file
        with open(file_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Extract and print the transcript
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        print("Transcription:")
        print(transcript)

        return transcript

    except Exception as e:
        print(f"Exception in transcribe_audio: {type(e).__name__}: {str(e)}")
        return None