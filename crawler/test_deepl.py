import os
from dotenv import load_dotenv
import deepl

load_dotenv()

auth_key = os.getenv("DEEPL_API_TOKEN")
translator = deepl.Translator(auth_key)

result = translator.translate_text("Hello, world!", target_lang="KO")
print(result.text)