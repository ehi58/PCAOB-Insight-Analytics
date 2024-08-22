from fastapi import FastAPI
import os
import subprocess
from starlette.responses import RedirectResponse

app = FastAPI()

@app.get("/")

def streamlit_app():
    subprocess.Popen(['streamlit', 'run', 'dashboard.py', '--server.port', '8501'])
    return RedirectResponse(url='/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)