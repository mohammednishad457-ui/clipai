from pathlib import Path
from uuid import uuid4
import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE=Path(__file__).resolve().parent
UPLOADS=BASE/"uploads"; CLIPS=BASE/"clips"
UPLOADS.mkdir(exist_ok=True); CLIPS.mkdir(exist_ok=True)
app=FastAPI(title="ClipAI API")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
app.mount("/clips",StaticFiles(directory=str(CLIPS)),name="clips")
jobs={}
ALLOWED={".mp4",".mov",".webm",".m4v"}

def process(job_id,path,seconds):
    try:
        jobs[job_id]["status"]="processing"
        probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
        total=float(probe.stdout.strip())
        starts=[0]
        if total>seconds*1.5: starts.append(max(0,(total-seconds)/2))
        if total>seconds*2.5: starts.append(max(0,total-seconds))
        result=[]
        for i,start in enumerate(dict.fromkeys(round(x,2) for x in starts),1):
            length=min(seconds,total-start)
            if length<1: continue
            name=f"{job_id}_{i}.mp4"; out=CLIPS/name
            subprocess.run(["ffmpeg","-y","-ss",str(start),"-i",str(path),"-t",str(length),"-c:v","libx264","-preset","veryfast","-c:a","aac","-movflags","+faststart",str(out)],capture_output=True,text=True,check=True)
            result.append({"name":f"Clip {i}","url":f"/clips/{name}","start":start,"duration":length})
        jobs[job_id].update(status="completed",clips=result)
    except Exception as e:
        jobs[job_id].update(status="failed",error=str(e))

@app.get("/")
def root(): return {"name":"ClipAI API","status":"running","docs":"/docs"}
@app.get("/api/health")
def health(): return {"status":"ok"}
@app.post("/api/jobs")
async def create_job(background_tasks:BackgroundTasks,video:UploadFile=File(...),clip_seconds:int=30):
    ext=Path(video.filename or "").suffix.lower()
    if ext not in ALLOWED: raise HTTPException(400,"Upload MP4, MOV, WebM or M4V.")
    if clip_seconds not in (15,30,60): raise HTTPException(400,"Choose 15, 30 or 60 seconds.")
    jid=str(uuid4()); path=UPLOADS/(jid+ext)
    size=0
    with path.open("wb") as f:
        while chunk:=await video.read(1024*1024):
            size+=len(chunk)
            if size>500*1024*1024:
                path.unlink(missing_ok=True); raise HTTPException(413,"Maximum file size is 500 MB.")
            f.write(chunk)
    jobs[jid]={"id":jid,"status":"queued","clips":[]}
    background_tasks.add_task(process,jid,path,clip_seconds)
    return {"job_id":jid,"status":"queued"}
@app.get("/api/jobs/{jid}")
def get_job(jid:str):
    if jid not in jobs: raise HTTPException(404,"Job not found")
    return jobs[jid]
