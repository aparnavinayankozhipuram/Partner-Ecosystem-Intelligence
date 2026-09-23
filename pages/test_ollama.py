import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2:3b",
        "prompt": "In one sentence, what does a partnership manager do?",
        "stream": False
    }
)

print(response.json()["response"])