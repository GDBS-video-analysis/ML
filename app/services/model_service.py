import os
import cv2
import tempfile
from datetime import timedelta
from deepface import DeepFace
import pandas as pd

def process_video_final(video_path, employee_folders):
    """
    Обрабатывает видео, сопоставляя найденные лица с папками сотрудников и сохраняет фотографии незнакомцев.

    :param video_path: Путь к видеофайлу.
    :param employee_folders: Словарь {ID сотрудника: путь до папки с фотографиями}.
    :return: Кортеж из двух словарей:
        - Словарь {ID сотрудника: список временных меток присутствия}.
        - Словарь {номер_незнакомца: {"path": путь_до_фото, "timestamps": [временные_метки]}}.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file '{video_path}' does not exist.")
    if not isinstance(employee_folders, dict):
        raise ValueError("employee_folders need to be dictionary { employee_id: employee_biometry_path}.")

    for folder in employee_folders.values():
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder with name '{folder}' didn't exist.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file with such path: '{video_path}'.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps)  # 1 кадр в секунду
    results = {}
    unknown_faces = {}
    counter = 1  # Счётчик для номеров незнакомцев
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Frames are over or reading error on frame: '{frame}")
            break

        if frame_id % frame_interval == 0:
            timestamp = str(timedelta(seconds=frame_id // fps))
            print(f"\nCurrent frame: {frame_id}")
            print(f"Current timestamp: {timestamp}")

            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame_file:
                    temp_frame_path = temp_frame_file.name
                    cv2.imwrite(temp_frame_path, frame)

                print(f"Analyzing this frame...")

                for employee_id, folder_path in employee_folders.items():
                    folder_path = os.path.normpath(folder_path)
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
                                    if timestamp not in results[employee_id]:
                                        results[employee_id].append(timestamp)
                                    print(f"An employee with id={employee_id} was found in the frame.")
                                    break
                        else:
                            print(f"No matches were found for the employee with id={employee_id}.")

                    except Exception as e:
                        print(f"Matching error for employee with id={employee_id}.\nError: {e}")

                # Обработка незнакомцев
                print(f"Looking for unknown faces...")
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)

                for (x, y, w, h) in faces:
                    face_img = frame[y:y + h, x:x + w]

                    unknown_face_found = False
                    face_id = None 

                    for employee_id, folder_path in employee_folders.items():

                        detections = DeepFace.find(
                            img_path=face_img,
                            db_path=folder_path,
                            enforce_detection=False,
                            silent=True
                        )
                        if isinstance(detections, list) and detections:
                            for detection in detections:
                                if isinstance(detection, pd.DataFrame) and not detection.empty:
                                    unknown_face_found = True
                                    break

                    if not unknown_face_found:

                        face_identified = False
                        for unknown_id, unknown_data in unknown_faces.items():

                            detected = DeepFace.find(
                                img_path=face_img,
                                db_path=unknown_data['path'],
                                enforce_detection=False,
                                silent=True
                            )
                            if isinstance(detected, list) and detected:
                                for detection in detected:
                                    if isinstance(detection, pd.DataFrame) and not detection.empty:
                                        unknown_face_found = True
                                        face_identified = True
                                        face_id = unknown_id
                                        break

                        if not face_identified:
                            unknown_face_folder = os.path.abspath(f"processing_data/unknown_faces/{counter}")
                            os.makedirs(unknown_face_folder, exist_ok=True)
                            unknown_face_path = os.path.join(unknown_face_folder, "face.jpg")
                            cv2.imwrite(unknown_face_path, face_img)

                            unknown_faces[counter] = {"path": unknown_face_folder, "timestamps": [timestamp]}
                            counter += 1
                        else:
                            unknown_faces[face_id]["timestamps"].append(timestamp)

                os.remove(temp_frame_path)

            except Exception as e:
                print(f"Frame processing error at the {timestamp} timestamp.\nError: {e}")

        frame_id += 1

    cap.release()
    return results, unknown_faces

# Поиск ТОЛЬКО сотрудников
def process_video(video_path, employee_folders):
    """
    Обрабатывает видео, сопоставляя найденные лица с папками сотрудников.

    :param video_path: Путь к видеофайлу.
    :param employee_folders: Словарь {ID сотрудника: путь до папки с фотографиями}.
    :return: Словарь {ID сотрудника: список временных меток присутствия}.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file '{video_path}' does not exist.")
    if not isinstance(employee_folders, dict):
        raise ValueError("employee_folders need to be dictionary { employee_id: employee_biometry_path}.")

    for folder in employee_folders.values():
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder with name '{folder}' didn't exist.")

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
            print(f"Frames are over or reading error on frame: '{frame}")
            break

        if frame_id % frame_interval == 0:
            timestamp = str(timedelta(seconds=frame_id // fps))
            print(f"\nCurrent frame: {frame_id}")
            print(f"Current timestamp: {timestamp}")

            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame_file:
                    temp_frame_path = temp_frame_file.name
                    cv2.imwrite(temp_frame_path, frame)

                print(f"Analyzing this frame...")

                for employee_id, folder_path in employee_folders.items():
                    folder_path = os.path.normpath(folder_path)
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
                                    if timestamp not in results[employee_id]:
                                        results[employee_id].append(timestamp)
                                    print(f"An employee with id={employee_id} was found in the frame.")
                                    break
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