from lms.config import Settings
from lms.setup_app import get_application

settings = Settings()
app = get_application(settings)
