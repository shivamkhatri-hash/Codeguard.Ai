import socket

import httpx
from google import genai

from app.core.config import settings


# Force hostname resolution to IPv4 for this test.
original_getaddrinfo = socket.getaddrinfo


def ipv4_getaddrinfo(*args, **kwargs):
    results = original_getaddrinfo(*args, **kwargs)
    return [result for result in results if result[0] == socket.AF_INET]


socket.getaddrinfo = ipv4_getaddrinfo


client = genai.Client(api_key=settings.GEMINI_API_KEY)

response = client.models.generate_content(
   model="gemini-3.6-flash",
    contents="Explain Cross-Site Scripting (XSS) in one sentence."
)

print("Gemini response:")
print(response.text)