from flask import Flask, json, jsonify
from deepface import DeepFace
import cv2
import os
from datetime import timedelta
import tempfile
import pandas as pd

app = Flask(__name__)

# Константы
test_data_path = "test_data/"
video_filename = "video.mp4"
db_path = os.path.join(test_data_path, "db")
video_path = os.path.join(test_data_path, video_filename)
results_storage_path = "results.json"


@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        # Открываем видео
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Ошибка: видеофайл не может быть открыт")
            return jsonify({"error": "Cannot open video file"}), 400

        print("Видео успешно открыто")
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps)  # 1 кадр в секунду
        results = {}
        frame_id = 0

        # Читаем видео кадр за кадром
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
                        # Здесь можно выбрать модель, лучшая это FaceNet512
                        img_path=temp_frame_path,
                        db_path=db_path,
                        enforce_detection=False,
                        silent=True
                    )

                    # Отладка
                    # print(f"Тип detections: {type(detections)}")
                    # print(f"Содержимое detections: {detections}")

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
            #print(f"Результаты для сохранения: {formatted_results}") 
            with open(results_storage_path, "w") as f:
                json.dump(formatted_results, f, indent=4)
            print(f"Результаты успешно записаны в файл {results_storage_path}")
        else:
            print("Результаты пусты, запись пропущена.")

        return jsonify({"message": "success", "results": results})

    except Exception as e:
        print(f"Ошибка в обработке видео: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/results', methods=['GET'])
def get_results():
    try:
        if os.path.exists(results_storage_path):
            with open(results_storage_path, "r") as f:
                results = json.load(f)
            print(f"Результаты загружены из {results_storage_path}")
            return jsonify(results)
        else:
            print("Файл результатов отсутствует")
            return jsonify({"error": "No results found. Process a video first."}), 404
    except Exception as e:
        print(f"Ошибка при чтении файла результатов: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)