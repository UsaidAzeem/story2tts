import io
import time
import soundfile as sf
from concurrent import futures

import argparse
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple

import gradio as gr
import grpc
import numpy as np
import soundfile as sf
import torch

import inference_pb2_grpc
from inference_pb2 import InferenceResponse

from inference_modules import load_model, run_inference

# load model once

class InferenceService(inference_pb2_grpc.InferenceServiceServicer):
    def GenerateAudio(self, request, context):
        try:
            # Load audio prompt from bytes
            audio_prompt = None
            if request.audio_prompt:
                data, samplerate = sf.read(io.BytesIO(request.audio_prompt), dtype="float32")
                audio_prompt = (samplerate, data)

            # Run inference
            sr, audio_output = run_inference(
                text_input=request.text_input,
                audio_prompt_input=audio_prompt,
                max_new_tokens=request.max_new_tokens,
                cfg_scale=request.cfg_scale,
                temperature=request.temperature,
                top_p=request.top_p,
                cfg_filter_top_k=request.cfg_filter_top_k,
                speed_factor=request.speed_factor,
            )

            # serialization for payload delivery
            with io.BytesIO() as buffer:
                sf.write(buffer, audio_output, sr, format='WAV')
                return InferenceResponse(audio_output=buffer.getvalue(), sample_rate=sr)

        except Exception as e:
            return InferenceResponse(audio_output=b'', sample_rate=0, error=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(InferenceService(), server)
    server.add_insecure_port('[::]:50051')     # grpc server port
    server.start()
    print("gRPC server listening on port 50051")
    server.wait_for_termination()

# class InferenceService(inference_pb2_grpc.InferenceServiceServicer):
#     ...
#     def ClearMemory(self, request, context):
#         try:
#             clear_inference_memory()
#             return inference_pb2.ClearMemoryResponse(status="Memory cleared.")
#         except Exception as e:
#             return inference_pb2.ClearMemoryResponse(status=f"Failed to clear memory: {str(e)}")

if __name__ == "__main__":
    load_model()
    serve()
