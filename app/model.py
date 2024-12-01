import os
import json
import cv2
from datetime import timedelta
import tempfile
from deepface import DeepFace
import pandas as pd
from app.build_intervals import build_intervals
from app.utils import generate_results_file_path

def process_video_file(video_path, biometry_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps)  # 1 кадр в секунду
    results = {}
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_interval == 0:
            timestamp = str(timedelta(seconds=frame_id // fps))
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame_file:
                temp_frame_path = temp_frame_file.name
                cv2.imwrite(temp_frame_path, frame)

            detections = DeepFace.find(
                img_path=temp_frame_path,
                db_path=biometry_path,  # Путь к базе данных лиц
                enforce_detection=False,
                silent=True
            )

            if isinstance(detections, list) and detections:
                for detection in detections:
                    if isinstance(detection, pd.DataFrame) and not detection.empty:
                        for _, row in detection.iterrows():
                            person_name = os.path.basename(row['identity']).split('.')[0]
                            if person_name not in results:
                                results[person_name] = []
                            if timestamp not in results[person_name]:
                                results[person_name].append(timestamp)
            os.remove(temp_frame_path)
        frame_id += 1
    cap.release()

    results_file = generate_results_file_path()
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    return results


def load_results(max_gap_minutes=5):
    results_file = generate_results_file_path()
    if not os.path.exists(results_file):
        raise FileNotFoundError("Results file does not exist")
    with open(results_file, "r") as f:
        raw_data = json.load(f) 
    processed_data = {
        employee: build_intervals(timestamps, max_gap_minutes) 
        for employee, timestamps in raw_data.items()
    }
    return processed_data