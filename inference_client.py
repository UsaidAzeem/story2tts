import gradio as gr
import grpc
import numpy as np
import io
import soundfile as sf

import inference_pb2_grpc
import inference_pb2

def clear_memory_grpc():
    try:
        response = stub.ClearMemory(inference_pb2.Empty())
        return response.status
    except grpc.RpcError as e:
        return f"Error: {e}"

def query_grpc_server(
    text_input,
    audio_prompt,
    max_new_tokens,
    cfg_scale,
    temperature,
    top_p,
    cfg_filter_top_k,
    speed_factor,
):
    try:
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = inference_pb2_grpc.InferenceServiceStub(channel)

            # Convert audio input to bytes
            audio_bytes = b""
            if audio_prompt is not None:
                sr, audio_np = audio_prompt
                with io.BytesIO() as buffer:
                    sf.write(buffer, audio_np, sr, format="WAV")
                    audio_bytes = buffer.getvalue()

            # Make gRPC request
            request = inference_pb2.InferenceRequest(
                text_input=text_input,
                audio_prompt=audio_bytes,
                max_new_tokens=max_new_tokens,
                cfg_scale=cfg_scale,
                temperature=temperature,
                top_p=top_p,
                cfg_filter_top_k=cfg_filter_top_k,
                speed_factor=speed_factor,
            )
            response = stub.GenerateAudio(request)

            if response.error:
                raise gr.Error(f"Inference error: {response.error}")

            # Convert response bytes to numpy
            audio_io = io.BytesIO(response.audio_output)
            audio_np, sr = sf.read(audio_io, dtype="int16")
            return (sr, audio_np)

    except grpc.RpcError as e:
        raise gr.Error(f"gRPC error: {e}")

#Gradio interface
iface = gr.Interface(
    fn=query_grpc_server,
    inputs=[
        gr.Textbox(label="Text Input"),
        gr.Audio(type="numpy", label="Audio Prompt"),
        gr.Slider(1, 20000, value=100, step=1, label="Max Tokens", info="Controls the maximum length of the generated audio (more tokens = longer audio)."),
        gr.Slider(1.0, 10.0, value=7.5, step=0.1, label="CFG Scale", info="Higher values increase adherence to the text prompt."),
        gr.Slider(0.1, 1.5, value=0.9, step=0.05, label="Temperature", info="Lower values make the output more deterministic, higher values increase randomness."),
        gr.Slider(0.5, 1.0, value=0.95, step=0.05, label="Top-p", info="Filters vocabulary to the most likely tokens cumulatively reaching probability P."),
        gr.Slider(1, 100, value=50, step=1, label="CFG Filter Top-K", info="Top k filter for CFG guidance."),
        gr.Slider(0.1, 2.0, value=1.0, step=0.1, label="Speed Factor", info="Adjusts the speed of the generated audio (1.0 = original speed)."),
    ],
    outputs=gr.Audio(label="Generated Audio"),
    title="Dia Inference Client (via gRPC)",
)

if __name__ == "__main__":
    iface.launch()

#if using blocks
# with gr.Blocks() as demo:
#     gr.Markdown("# Dia Inference Client (via gRPC)")

#     with gr.Row():
#         text_input = gr.Textbox(label="Text Input")
#         audio_input = gr.Audio(type="numpy", label="Audio Prompt")

#     with gr.Row():
#         max_tokens = gr.Slider(1, 20000, value=100, step=1, label="Max Tokens")
#         cfg_scale = gr.Slider(1.0, 10.0, value=7.5, step=0.1, label="CFG Scale")
#         temperature = gr.Slider(0.1, 1.5, value=0.9, step=0.05, label="Temperature")
#         top_p = gr.Slider(0.5, 1.0, value=0.95, step=0.05, label="Top-p")
#         cfg_filter_top_k = gr.Slider(1, 100, value=50, step=1, label="CFG Filter Top-K")
#         speed_factor = gr.Slider(0.1, 2.0, value=1.0, step=0.1, label="Speed Factor")

#     output_audio = gr.Audio(label="Generated Audio")
#     status_output = gr.Textbox(label="Status", interactive=False)

#     with gr.Row():
#         gr.Button("Generate").click(
#             fn=query_grpc_server,
#             inputs=[
#                 text_input, audio_input,
#                 max_tokens, cfg_scale, temperature,
#                 top_p, cfg_filter_top_k, speed_factor
#             ],
#             outputs=output_audio,
#         )
#         gr.Button("Clear Memory").click(
#             fn=clear_memory_grpc,
#             outputs=status_output
#         )

#     gr.Markdown("Generated audio appears above. Clear memory to free up inference cache.")

# if __name__ == "__main__":
#     demo.launch()

