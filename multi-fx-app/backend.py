from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import asyncio
import os
import subprocess

app = FastAPI()
process = None  # the live effect subprocess (main.py), started by /start-effects
record_process = None  # the raw-recording subprocess (record.py)

RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

@app.get("/start-effects")
async def start_effects(request: Request):
    global process, record_process
    try:
        # Stop any effect that is already running before starting a new one
        if process and process.poll() is None:
            process.terminate()
            process = None

        # A raw recording and a live effect can't use the mic at the same time
        if record_process and record_process.poll() is None:
            record_process.terminate()
            record_process = None

        params = request.query_params

        # Parse query parameters
        args = [
            "python3", "main.py",
            "--volume", params.get("volume", "0"),
            "--gain", params.get("gain", "0"),
            "--wetDry", params.get("wetDry", "0"),
            "--enableDistortion", params.get("enableDistortion", "false"),
            "--chorusLevel", params.get("chorusLevel", "0"),
            "--chorusRate", params.get("chorusRate", "0"),
            "--chorusDepth", params.get("chorusDepth", "0"),
            "--enableChorus", params.get("enableChorus", "false"),
            "--delayLevel", params.get("delayLevel", "0"),
            "--feedback", params.get("feedback", "0"),
            "--delay", params.get("delay", "0"),
            "--enableDelay", params.get("enableDelay", "false"),
        ]

        # Start main.py as a subprocess
        process = subprocess.Popen(args)
        return JSONResponse(content={"status": "started"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/stop-effects")
def stop_effects():
    global process
    try:
        if process and process.poll() is None:
            process.terminate()
            process = None
            return JSONResponse(content={"status": "stopped"}, status_code=200)
        else:
            return JSONResponse(content={"status": "not running"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/record/start")
async def start_recording():
    global record_process, process
    try:
        # Stop any raw recording already in progress before starting a new one
        if record_process and record_process.poll() is None:
            record_process.terminate()
            record_process = None

        # A live effect and a raw recording can't use the mic at the same time
        if process and process.poll() is None:
            process.terminate()
            process = None

        record_process = subprocess.Popen(["python3", "record.py"])
        return JSONResponse(content={"status": "recording"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/record/stop")
def stop_recording():
    global record_process
    try:
        if record_process and record_process.poll() is None:
            record_process.terminate()
            record_process = None
            return JSONResponse(content={"status": "stopped"}, status_code=200)
        else:
            return JSONResponse(content={"status": "not recording"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/process-recording")
async def process_recording(request: Request):
    try:
        dry_path = os.path.join(RECORDINGS_DIR, "dry_latest.wav")
        if not os.path.exists(dry_path):
            return JSONResponse(
                content={"error": "No recording to process yet. Record something first."},
                status_code=400,
            )

        params = request.query_params
        args = [
            "python3", "process_recording.py",
            "--volume", params.get("volume", "0"),
            "--gain", params.get("gain", "0"),
            "--wetDry", params.get("wetDry", "0"),
            "--enableDistortion", params.get("enableDistortion", "false"),
            "--chorusLevel", params.get("chorusLevel", "0"),
            "--chorusRate", params.get("chorusRate", "0"),
            "--chorusDepth", params.get("chorusDepth", "0"),
            "--enableChorus", params.get("enableChorus", "false"),
            "--delayLevel", params.get("delayLevel", "0"),
            "--feedback", params.get("feedback", "0"),
            "--delay", params.get("delay", "0"),
            "--enableDelay", params.get("enableDelay", "false"),
        ]

        # Offline batch processing is bounded (unlike the live effect loop),
        # so it's safe to wait for it to finish before responding. Run it in
        # a thread so we don't block the event loop while it works.
        result = await asyncio.to_thread(
            subprocess.run, args, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return JSONResponse(
                content={"error": result.stderr.strip() or "Processing failed"},
                status_code=500,
            )

        return JSONResponse(content={"status": "processed"}, status_code=200)
    except subprocess.TimeoutExpired:
        return JSONResponse(content={"error": "Processing timed out"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def _recording_response(filename):
    path = os.path.join(RECORDINGS_DIR, filename)
    if not os.path.exists(path):
        return JSONResponse(content={"error": "No recording available yet"}, status_code=404)
    return FileResponse(
        path,
        media_type="audio/wav",
        filename=filename,
        headers={"Cache-Control": "no-store"},
    )

@app.get("/recordings/dry")
def get_dry_recording():
    # The unprocessed microphone input from the most recent recording
    return _recording_response("dry_latest.wav")

@app.get("/recordings/wet")
def get_wet_recording():
    # The effect-processed output from the most recent effect run or Process Recording
    return _recording_response("wet_latest.wav")
