from openai import OpenAI
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()
client = OpenAI()


completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Sabes de python?."
        }
    ]
)

print(completion.choices[0].message)
