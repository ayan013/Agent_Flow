from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
import base64
from pathlib import Path

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

prompt = """
ONE isolated full-body 17th-century Maratha warrior,
braced while climbing a vertical cliff using a hemp rope.

Photorealistic cinematic reconstruction.
Three-quarter rear view, physically believable climbing posture.
Dark turban, simple cotton tunic, dhoti, cloth sash.
Cool blue-gray moonlight from upper left.

Entire character visible, including hands and feet.
Transparent background, clean alpha edges.
NO scenery, rock wall, text, collage, panels or asset sheet.
Exactly ONE character.
"""

response = client.images.generate(
    model="gpt-image-2.5-sunburst",
    prompt=prompt,
    size="1024x1536",
    quality="high",
    background="transparent",
    output_format="png",
    n=1
)

path = Path("s05_mavla01_braced.png")
path.write_bytes(base64.b64decode(response.data[0].b64_json))

image = Image.open(path)
print("Saved:", path)
print("Mode:", image.mode)
print("Has transparency:", image.getextrema()[3][0] < 255 if image.mode == "RGBA" else False)
