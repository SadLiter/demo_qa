import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

AUTH_DATA = {
    "email": os.getenv("SUPER_ADMIN_EMAIL"),
    "password": os.getenv("SUPER_ADMIN_PASSWORD"),
}

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
AUTH_API_BASE_URL = os.getenv("AUTH_API_BASE_URL")
MOVIES_API_BASE_URL = os.getenv("MOVIES_API_BASE_URL")

