import os
from TTS.api import TTS

# Initialize TTS model
model_name = "tts_models/en/ljspeech/tacotron2-DDC_ph"
tts = TTS(model_name, progress_bar=True, gpu=False)

def generate_audio(text):
    # Generate the speech (NumPy array)
    audio = tts.tts(text)
    
    # Define the audio file path
    audio_path = "generated_audio.wav"
    
    # Save the audio to a WAV file using the Soundfile library
    import soundfile as sf
    sf.write(audio_path, audio, samplerate=tts.synthesizer.output_sample_rate)
    
    return audio_path
