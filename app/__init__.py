from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from app.database import ScheduleManager

def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # load function
    app.register_blueprint(webhook_blueprint)
    ScheduleManager().__init__()

    return app
