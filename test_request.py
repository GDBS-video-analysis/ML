import requests

response = requests.post("http://127.0.0.1:5000/process_video")

if response.status_code == 200:
    print("Success! Json file:")
    print(response.json())
else:
    print(f"Ошибка: {response.status_code}")
    print("Ответ сервера:", response.text)