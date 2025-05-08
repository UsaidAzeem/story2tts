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

from dia.dia.model import Dia

# def clear_inference_memory():
#     """
#     Frees PyTorch cache and collects garbage to clear inference-related memory.
#     Does not unload the model.
#     """
#     import gc
#     gc.collect()
#     if torch.cuda.is_available():
#         torch.cuda.empty_cache()
#         torch.cuda.ipc_collect()
#     print("Cleared inference memory (but model remains loaded).")


def load_model():
    """  
    loads the model onto mem | expects nothing | returns nothing | prints results
    """

    global model, device   # global model, vars for reproducibility
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    print("Loading Nari model...")
    try:
        # Uses the function from inference.py
        model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16", device=device)
        print("model ready")
    except Exception as e:
        print(f"Error loading Nari model: {e}")
        raise
        
def run_inference(
    text_input: str,
    audio_prompt_input: Optional[Tuple[int, np.ndarray]],
    max_new_tokens: int,
    cfg_scale: float,
    temperature: float,
    top_p: float,
    cfg_filter_top_k: int,
    speed_factor: float,
):
    global model, tokenizer  # use the globally loaded model

    if not text_input or text_input.isspace():
        raise gr.Error("Text input cannot be empty.")

    temp_txt_file_path = None
    temp_audio_prompt_path = None
    output_audio = (44100, np.zeros(1, dtype=np.float32))

    try:
        prompt_path_for_generate = None
        if audio_prompt_input is not None:
            sr, audio_data = audio_prompt_input
            if audio_data is None or audio_data.size == 0 or audio_data.max() == 0:
                gr.Warning("Audio prompt seems empty or silent, ignoring prompt.")
            else:
                with tempfile.NamedTemporaryFile(mode="wb", suffix=".wav", delete=False) as f_audio:
                    temp_audio_prompt_path = f_audio.name

                    if np.issubdtype(audio_data.dtype, np.integer):
                        max_val = np.iinfo(audio_data.dtype).max
                        audio_data = audio_data.astype(np.float32) / max_val
                    elif not np.issubdtype(audio_data.dtype, np.floating):
                        gr.Warning(f"Unsupported audio prompt dtype {audio_data.dtype}, attempting conversion.")
                        try:
                            audio_data = audio_data.astype(np.float32)
                        except Exception as conv_e:
                            raise gr.Error(f"Failed to convert audio prompt to float32: {conv_e}")

                    if audio_data.ndim > 1:
                        if audio_data.shape[0] == 2:
                            audio_data = np.mean(audio_data, axis=0)
                        elif audio_data.shape[1] == 2:
                            audio_data = np.mean(audio_data, axis=1)
                        else:
                            gr.Warning(f"Audio prompt has unexpected shape {audio_data.shape}, taking first channel/axis.")
                            audio_data = (
                                audio_data[0] if audio_data.shape[0] < audio_data.shape[1] else audio_data[:, 0]
                            )
                        audio_data = np.ascontiguousarray(audio_data)

                    try:
                        sf.write(
                            temp_audio_prompt_path, audio_data, sr, subtype="FLOAT"
                        )
                        prompt_path_for_generate = temp_audio_prompt_path
                        print(f"Created temporary audio prompt file: {temp_audio_prompt_path} (orig sr: {sr})")
                    except Exception as write_e:
                        print(f"Error writing temporary audio file: {write_e}")
                        raise gr.Error(f"Failed to save audio prompt: {write_e}")

        # generate
        start_time = time.time()

        with torch.inference_mode():
            output_audio_np = model.generate(
                text_input,
                max_tokens=max_new_tokens,
                cfg_scale=cfg_scale,
                temperature=temperature,
                top_p=top_p,
                cfg_filter_top_k=cfg_filter_top_k,
                use_torch_compile=False,
                audio_prompt=prompt_path_for_generate,
            )

        end_time = time.time()
        print(f"Generation finished in {end_time - start_time:.2f} seconds.")

        # convert codes to audio
        if output_audio_np is not None:
            output_sr = 44100
            original_len = len(output_audio_np)
            speed_factor = max(0.1, min(speed_factor, 5.0))
            target_len = int(original_len / speed_factor)
            if target_len != original_len and target_len > 0:
                x_original = np.arange(original_len)
                x_resampled = np.linspace(0, original_len - 1, target_len)
                resampled_audio_np = np.interp(x_resampled, x_original, output_audio_np)
                output_audio = (
                    output_sr,
                    resampled_audio_np.astype(np.float32),
                )
                print(f"Resampled audio from {original_len} to {target_len} samples for {speed_factor:.2f}x speed.")
            else:
                output_audio = (
                    output_sr,
                    output_audio_np,
                )
                print(f"Skipping audio speed adjustment (factor: {speed_factor:.2f}).")

            print(f"Audio conversion successful. Final shape: {output_audio[1].shape}, Sample Rate: {output_sr}")

            if output_audio[1].dtype == np.float32 or output_audio[1].dtype == np.float64:
                audio_for_gradio = np.clip(output_audio[1], -1.0, 1.0)
                audio_for_gradio = (audio_for_gradio * 32767).astype(np.int16)
                output_audio = (output_sr, audio_for_gradio)
                print("Converted audio to int16 for Gradio output.")
        else:
            print("\nGeneration finished, but no valid tokens were produced.")
            gr.Warning("Generation produced no output.")
    except Exception as e:
        print(f"Error during inference: {e}")
        import traceback
        traceback.print_exc()
        raise gr.Error(f"Inference failed: {e}")

    finally:
        # cleanup
        if temp_txt_file_path and Path(temp_txt_file_path).exists():
            try:
                Path(temp_txt_file_path).unlink()
                print(f"Deleted temporary text file: {temp_txt_file_path}")
            except OSError as e:
                print(f"Warning: Error deleting temporary text file {temp_txt_file_path}: {e}")
        if temp_audio_prompt_path and Path(temp_audio_prompt_path).exists():
            try:
                Path(temp_audio_prompt_path).unlink()
                print(f"Deleted temporary audio prompt file: {temp_audio_prompt_path}")
            except OSError as e:
                print(f"Warning: Error deleting temporary audio prompt file {temp_audio_prompt_path}: {e}")

    return output_audio