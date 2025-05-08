import streamlit as st
import grpc
import base64
import tempfile
import tts_service_pb2
import tts_service_pb2_grpc

st.title("🗣️ Story2Audio Generator")

# Connect to gRPC server
channel = grpc.insecure_channel("localhost:50051")
stub = tts_service_pb2_grpc.TextToSpeechStub(channel)

# Input
story_text = st.text_area("Enter your story here", height=200)
file = st.file_uploader("Or upload a .txt file", type=["txt"])
if file:
    story_text = file.read().decode("utf-8")

if st.button("Generate Audio") and story_text.strip():
    with st.spinner("Generating audio..."):
        try:
            request = tts_service_pb2.TextRequest(text=story_text)
            response = stub.GenerateAudio(request)

            if response.status == "success":
                audio_bytes = base64.b64decode(response.audio_base64)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name
                st.audio(tmp_path, format="audio/wav")
                st.success(response.message)
            else:
                st.error(response.message)
        except grpc.RpcError as e:
            st.error(f"gRPC Error: {e.details()}")

