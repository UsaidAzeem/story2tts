import unittest
import grpc
import time
from concurrent import futures
from tts_service_pb2_grpc import add_TextToSpeechServicer_to_server, TextToSpeechStub
from tts_service_pb2 import TextRequest, AudioResponse
from server import TextToSpeechServicer  # Your gRPC servicer class
import multiprocessing

def run_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TextToSpeechServicer_to_server(TextToSpeechServicer(), server)  # Fix the typo here
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

class TestTextToSpeechService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_process = multiprocessing.Process(target=run_server)
        cls.server_process.start()
        time.sleep(1)  # Give the server a second to start

        cls.channel = grpc.insecure_channel('localhost:50051')
        cls.stub = TextToSpeechStub(cls.channel)

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.join()

    def test_valid_text(self):
        request = TextRequest(text="Hello world")
        response = self.stub.GenerateAudio(request)
        self.assertTrue(response.audio_base64)  # Correct this line to use audio_base64

    def test_empty_text(self):
        request = TextRequest(text="")
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.GenerateAudio(request)
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)

if __name__ == '__main__':
    unittest.main()
