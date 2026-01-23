FROM python:3.10-slim-buster
RUN apt-get update && apt-get install -y ffmpeg git
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"] 
