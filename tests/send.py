import base64
import requests
from pathlib import Path

if __name__ == '__main__':
    p = Path("./static/2_1.jpg")
    with open(p, "rb") as imageFile:
        imageStr = base64.b64encode(imageFile.read()).decode('utf-8')

    a = requests.post('http://localhost:5000/image/recognize', json={'photo': imageStr})
    print(a.json())

