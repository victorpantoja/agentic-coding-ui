from app.app import create_app
from app.config import settings

app = create_app(debug=settings.debug)
