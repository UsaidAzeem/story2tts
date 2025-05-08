import grpc
import tts_service_pb2
import tts_service_pb2_grpc
import base64
import os

def generate_audio_from_text(text):
    # Connect to the gRPC server with increased message size limit
    channel = grpc.insecure_channel('localhost:50051', 
                                    options=[('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
                                             ('grpc.max_receive_message_length', 50 * 1024 * 1024)])  # 50 MB
    stub = tts_service_pb2_grpc.TextToSpeechStub(channel)

    # Prepare the request
    request = tts_service_pb2.TextRequest(text=text)

    # Call the gRPC service
    response = stub.GenerateAudio(request)

    if response.status == "success":
        print(response.message)

        # Decode the base64 audio data
        audio_data = base64.b64decode(response.audio_base64)

        # Save the audio data to a WAV file
        audio_file_path = "generated_audio.wav"
        with open(audio_file_path, "wb") as f:
            f.write(audio_data)

        # Play the audio (simple method using wave module)
        os.system(f"start {audio_file_path}")  # This works on Windows

    else:
        print(f"Error: {response.message}")
        return None


# Example usage: Read from a text file
if __name__ == "__main__":
    file_path = input("Enter the file path containing the story/text: ")
    try:
        with open(file_path, 'r') as file:
            story_text = file.read()
            generate_audio_from_text(story_text)
    except FileNotFoundError:
        print("The file does not exist.")
