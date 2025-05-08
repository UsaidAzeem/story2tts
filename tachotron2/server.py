import grpc
from concurrent import futures
import time
import tts_service_pb2
import tts_service_pb2_grpc
import base64
from tts_engine import generate_audio  # Assume this function generates and saves audio

class TextToSpeechServicer(tts_service_pb2_grpc.TextToSpeechServicer):
    def GenerateAudio(self, request, context):
        text = request.text
        if not text:
            context.set_details("Invalid input")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return tts_service_pb2.AudioResponse(status="error", message="Text cannot be empty", audio_base64="")

        try:
            # Generate the audio and get the file path
            audio_path = generate_audio(text)  # Assume this function returns the path to the saved audio file
            
            # Read the audio file and encode it in base64
            with open(audio_path, "rb") as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")

            return tts_service_pb2.AudioResponse(status="success", message="Audio generated successfully", audio_base64=audio_base64)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return tts_service_pb2.AudioResponse(status="error", message="Failed to generate audio", audio_base64="")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), 
                         options=[('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
                                  ('grpc.max_receive_message_length', 50 * 1024 * 1024)])  # 50 MB
    tts_service_pb2_grpc.add_TextToSpeechServicer_to_server(TextToSpeechServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server starting...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # Keep server alive
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
