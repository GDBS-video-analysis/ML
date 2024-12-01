# Запуск локалки с моделью

from app import create_app
print("Запуск сервера...")
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    print("Сервер запущен.")