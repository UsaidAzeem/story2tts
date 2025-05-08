# Dia-TTS: Text-to-Speech Server with Gradio Front-End
This repository provides a solution for building a Text-to-Speech (TTS) server using Dia 1.6B via gRPC and a Gradio-based web interface. With this setup, you can easily run a fully functional TTS system both online and offline.

#### Requirements
Python 3.7+

Git

Docker (optional for Docker-based deployment)

#### Setup Instructions
1. Set Up the Python Environment
Create and activate a Python virtual environment:

bash
Copy
Edit
# Create a virtual environment
python -m venv 'env_name'

# Activate the environment
source env_name/bin/activate  # For macOS/Linux
env_name\Scripts\activate    # For Windows
2. Clone the Repository
Clone the Dia base repository:

bash
Copy
Edit
git clone https://github.com/nari-labs/dia
cd dia
3. Install Dia Dependencies
Install dependencies required by Dia:

bash
Copy
Edit
pip install -e .
4. Install Application Dependencies
Install the dependencies required for the application:

bash
Copy
Edit
pip install -r requirements.txt
5. Run the Server
Start the inference server:

bash
Copy
Edit
python inference_server.py
6. Run the Gradio Front-End
Launch the Gradio front-end to interact with the TTS server:

bash
Copy
Edit
python inference_client.py
Alternative Deployment (Docker)
If you prefer to use Docker, you have the option to choose between the following images:

docker.base: A larger, offline-capable image for a complete environment.

docker.runtime: A smaller, online-only image with a lightweight setup.

To build and deploy with Docker:

bash
Copy
Edit
# Build the Docker base image (large/offline)
docker build -t dia-tts-base -f Dockerfile.base .

# Build the Docker runtime image (small/online)
docker build -t dia-tts-runtime -f Dockerfile.runtime .
Project Structure
inference_server.py: The gRPC-based server that handles TTS requests.

inference_client.py: The Gradio front-end for user interaction.

requirements.txt: The dependencies for the application.

Dockerfile.base: Dockerfile for building a full offline-capable environment.

Dockerfile.runtime: Dockerfile for building a smaller, online runtime environment.

Notes
Ensure that all the dependencies are installed in your Python environment for the system to function correctly.

The gRPC server and Gradio front-end can be customized to suit your needs.
