import base64
from openai import OpenAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = r"Screenshot 2025-03-24 111132.png"

# Getting the Base64 string
base64_image = encode_image(image_path)

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

completion = client.chat.completions.create(
  model="olmocr-7b-0225-preview",
  messages=[
    
    {
        "role": "user", 
        "content": [                    
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
     }
  ],
  temperature=0.7,
)

print(completion.choices[0].message)