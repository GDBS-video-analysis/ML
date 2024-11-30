from flask import Flask
from app.routes import video_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(video_bp)

    return app