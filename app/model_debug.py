import os
import json
import shutil
from typing import Dict, List
import cv2
from datetime import timedelta
import tempfile
from deepface import DeepFace
import pandas as pd

def process_video_with_employees(video_path, employee_folders):
    """
    Обрабатывает видео, сопоставляя найденные лица с папками сотрудников.
    
    :param video_path: Путь к видеофайлу.
    :param employee_folders: Словарь {ID сотрудника: путь до папки с фотографиями}.
    :return: Словарь {ID сотрудника: список временных меток присутствия}.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file '{video_path}' does not exist.")
    if not isinstance(employee_folders, dict):
        raise ValueError("employee_folders need to be dictionary { emloyee_id: employee_biometry_path}.")

    for folder in employee_folders.values():
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder with name '{folder}' didnt exist.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file with such path: '{video_path}'.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps)  # 1 кадр в секунду
    results = {}
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Frames is over or reading error on frame: '{frame}")
            break

        if frame_id % frame_interval == 0:  # Обрабатываем 1 кадр в секунду
            timestamp = str(timedelta(seconds=frame_id // fps))
            print(f"\nCurrent frame: {frame_id}")
            print(f"Current timestamp: {timestamp}")

            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame_file:
                    temp_frame_path = temp_frame_file.name
                    cv2.imwrite(temp_frame_path, frame)

                print(f"Analyzing this frame...")

                for employee_id, folder_path in employee_folders.items():
                    folder_path = os.path.normpath(folder_path)  # Приведение пути к корректному виду
                    print(f"Analyzing employee with id={employee_id} on frame...")

                    try:
                        detections = DeepFace.find(
                            img_path=temp_frame_path,
                            db_path=folder_path,
                            enforce_detection=False,
                            silent=True
                        )

                        if isinstance(detections, list) and detections:
                            for detection in detections:
                                if isinstance(detection, pd.DataFrame) and not detection.empty:
                                    if employee_id not in results:
                                        results[employee_id] = []
                                    if timestamp not in results[employee_id]:  # Избегаем дублирования
                                        results[employee_id].append(timestamp)
                                    print(f"An employee with id={employee_id} was found in the frame.")
                                    break  # Прерываем, если сотрудник найден
                                # Бесполезная по сути проверка, которая только засоряет код,
                                # но если что-нибудь сломается ее можно раскомментить.
                                #else:
                                    #print(f"Empty DataFrame or invalid data for ID={employee_id}.")
                        else:
                            print(f"No matches were found for the employee with id={employee_id}.")

                    except Exception as e:
                        print(f"Matching error for employee with id={employee_id}.\nError: {e}")

                os.remove(temp_frame_path)

            except Exception as e:
                print(f"Frame processing error at the {timestamp} timestamp.\nError: {e}")

        frame_id += 1

    cap.release()
    return results

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
