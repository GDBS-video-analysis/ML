FROM tensorflow/tensorflow:2.12.0 AS builder
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"]