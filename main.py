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
    # 1. Unique ID aur Folder setup
    user_id = bot_token.split(":")[0]
    repo_url = "https://github.com/Gxinfinity/Bot_Deploy.git"
    path = f"./bots/{user_id}"

    try:
        # Puraana folder saaf karein agar hai toh
        if os.path.exists(path):
            shutil.rmtree(path)
        
        # 2. GitHub se code clone karein
        os.system(f"git clone {repo_url} {path}")

        # 3. Docker Image Build karein (Local build)
        image_tag = f"bot_image_{user_id}"
        print(f"Building image: {image_tag}")
        image, logs = docker_client.images.build(path=path, tag=image_tag, rm=True)

        # 4. Container Run karein (Restart Always ke saath)
        container_name = f"tg_bot_{user_id}"
        
        # Purana container stop karein agar wahi bot firse deploy ho raha hai
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
        return {"status": "success", "message": f"Bhai, {category} Bot Live ho gaya!", "container_id": container.short_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}
