import os
import json
import cv2
from datetime import timedelta
import tempfile
from deepface import DeepFace
import pandas as pd
from app.utils import generate_results_file_path


def process_video_file_debug(video_path, db_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file '{video_path}' does not exist.")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database path '{db_path}' does not exist.")

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
            print("Кадры закончились или произошла ошибка чтения")
            break

        if frame_id % frame_interval == 0:  # Обрабатываем 1 кадр в секунду
            timestamp = str(timedelta(seconds=frame_id // fps))
            print(f"Обрабатывается кадр: {frame_id}")
            print(f"Обрабатывается временная метка: {timestamp}")

            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame_file:
                    temp_frame_path = temp_frame_file.name
                    cv2.imwrite(temp_frame_path, frame)

                print(f"Ищем лица в кадре...")
                detections = DeepFace.find(
                    img_path=temp_frame_path,
                    db_path=db_path,
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
                                if timestamp not in results[person_name]:  # Избегаем дублирования
                                    results[person_name].append(timestamp)
                                print(f"На кадре был обнаружен {person_name}.")
                        else:
                            print("Пустой DataFrame или некорректные данные в списке.")
                else:
                    print("Совпадения не найдены или результат имеет неверный формат.")
                os.remove(temp_frame_path)

            except Exception as e:
                print(f"Ошибка обработки кадра на временной метке {timestamp}: {e}")

        frame_id += 1

    cap.release()

    if results:
        formatted_results = {person: {"timestamps": times} for person, times in results.items()}
        print(f"Результаты для сохранения: {formatted_results}") 
        results_file = generate_results_file_path()
        with open(results_file, "w") as f:
            json.dump(results, f, indent=4)
        return results
    else:
        print("Результаты пусты, запись пропущена.")

    return results