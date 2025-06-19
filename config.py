from dotenv import load_dotenv
import os

def get_local_ip():
    load_dotenv(override=True)  # Force reload .env
    return os.getenv("IP_ADDRESS")

LOCAL_IP = get_local_ip()