import os
import requests
from dotenv import load_dotenv

load_dotenv()


def translate_text(text: str, source: str = "en", target: str = "ru"):
    try:
        url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        payload = {
            "q": text,
            "source": source,
            "target": target
        }
        headers = {
            "x-rapidapi-key": os.getenv("DEEP_TRANSLATE_API_KEY"),
            "x-rapidapi-host": "deep-translate1.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        response = requests.post(url,
                                 json=payload, headers=headers, timeout=10)
        return response.json()["data"]["translations"]["translatedText"][0]
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")
