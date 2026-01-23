from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import docker
import os
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")
docker_client = docker.from_env()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/deploy")
async def deploy_bot(
    category: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    bot_token: str = Form(...),
    owner_id: str = Form(...),
    session: str = Form("")
):
    # ERROR FIX: Docker tags must be lowercase
    user_id = bot_token.split(":")[0].lower() 
    repo_url = "https://github.com/Gxinfinity/Bot_Deploy.git"
    path = f"./bots/{user_id}"

    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        
        os.system(f"git clone {repo_url} {path}")

        # Fix: Tag is now lowercase
        image_tag = f"bot_image_{user_id}".lower() 
        image, logs = docker_client.images.build(path=path, tag=image_tag, rm=True)

        container_name = f"tg_bot_{user_id}".lower()
        
        try:
            old_container = docker_client.containers.get(container_name)
            old_container.stop()
            old_container.remove()
        except:
            pass

        container = docker_client.containers.run(
            image.id,
            detach=True,
            name=container_name,
            restart_policy={"Name": "always"},
            environment={
                "API_ID": api_id,
                "API_HASH": api_hash,
                "BOT_TOKEN": bot_token,
                "OWNER_ID": owner_id,
                "STRING_SESSION": session
            }
        )
        return {"status": "success", "message": "Bhai, App se Bot Deploy ho gaya!", "id": container.short_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}
