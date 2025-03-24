import base64
from openai import OpenAI
from olmocr.data.renderpdf import render_pdf_to_base64png
from olmocr.prompts import build_finetuning_prompt
from olmocr.prompts.anchor import get_anchor_text


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = r"Screenshot 2025-03-24 111132.png"

# Getting the Base64 string
base64_image = encode_image(image_path)

# Render page 1 to an image
#image_base64 = render_pdf_to_base64png("./paper.pdf", 1, target_longest_image_dim=1024)

# Build the prompt, using document metadata
anchor_text = get_anchor_text("./2024-P6-Maths-Prelim Exam-ACSJ.pdf", 2, pdf_engine="pdfreport", target_length=4000)
prompt = build_finetuning_prompt(anchor_text)

print(prompt)

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

completion = client.chat.completions.create(
  model="olmocr-7b-0225-preview",
  messages=[
    
    {
        "role": "user", 
        "content": [                    
                    {"type": "text", "text": prompt},
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