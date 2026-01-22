from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import docker

app = FastAPI()
templates = Jinja2Templates(directory="templates")
docker_client = docker.from_env()

# Home Page (Jaha form dikhega)
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Deployment Logic
@app.post("/deploy")
async def deploy_bot(
    category: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    bot_token: str = Form(...),
    owner_id: str = Form(...),
    session: str = Form("")
):
    # Image select karein category ke basis par
    images = {
        "Music": "your-hub/music-bot",
        "Games": "your-hub/game-bot",
        "Chatbot": "your-hub/chatbot"
    }
    
    env_vars = {
        "API_ID": api_id,
        "API_HASH": api_hash,
        "BOT_TOKEN": bot_token,
        "OWNER_ID": owner_id,
        "STRING_SESSION": session
    }

    try:
        # Docker container start karein
        container = docker_client.containers.run(
            image=images[category],
            detach=True,
            environment=env_vars,
            restart_policy={"Name": "always"} # Yeh bot ko kabhi band nahi hone dega
        )
        return {"status": "success", "message": f"Bhai, {category} Bot live ho gaya!", "id": container.short_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}
