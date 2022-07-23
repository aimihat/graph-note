import uvicorn
from api.main import app
import logging
import subprocess

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Start a child process to run the UI.
    subprocess.Popen(["npm", "start", "--prefix", "app"])

    # Start the FastAPI server.
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, debug=True)
