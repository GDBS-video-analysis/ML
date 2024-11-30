import requests

video_path = "tests/test_data/video.mp4"
biometry_path = "tests/test_data/db"

response = requests.post("http://127.0.0.1:5000/process_video",
    json={"video_path": video_path, "biometry_path": biometry_path})

if response.status_code == 200:
    print("Success! Json file:")
    print(response.json())
else:
    print(f"Ошибка: {response.status_code}")
    print("Ответ сервера:", response.text)