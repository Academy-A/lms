from src.config import Settings
from src.setup_app import get_application

settings = Settings()
app = get_application(settings)
