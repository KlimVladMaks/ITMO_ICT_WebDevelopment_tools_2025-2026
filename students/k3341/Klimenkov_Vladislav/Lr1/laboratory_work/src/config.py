import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('TG_BOT_TOKEN')
