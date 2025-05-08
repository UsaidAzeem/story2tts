import gradio as gr
import grpc
from tts_service_pb2 import TextRequest
from tts_service_pb2_grpc import TextToSpeechStub
import tempfile
import base64

def generate_audio(text):
    # Connect to the gRPC server
    channel = grpc.insecure_channel('localhost:50051')
    stub = TextToSpeechStub(channel)
    request = TextRequest(text=text)
    response = stub.GenerateAudio(request)
    
    # Check if the response is successful
    if response.status == "success":
        audio_data = response.audio_base64
        
        # Decode the base64 audio data
        decoded_audio = base64.b64decode(audio_data)
        
        # Save the decoded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(decoded_audio)  # Write the decoded audio to the file
            return temp_file.name  # Return the file path for Gradio to play
        
    else:
        return "Error: " + response.message

# Set up Gradio interface
iface = gr.Interface(fn=generate_audio,
                     inputs=gr.Textbox(label="Enter Text for Audio"),
                     outputs=gr.Audio(label="Generated Audio"))

iface.launch()
