import base64
import os
from google import genai
from google.genai import types
import tempfile
import pymupdf
import json
import os
import glob
from pathlib import Path

SYSTEM_PROMPT="""You are an OCR machine designed to parse Exam Papers. Your job is to look at the image of an exam paper and detect the 2d bounding box of each question in the image as bbox, with the question number as the label and the text of the question as text and the topic as topic. For topic, pick only from the list of TOPICS that is described below.

Each question will start with a number and may have images, charts and tables. Make sure the bbox coordinates covers both the question as well as the charts and images.

If there are sub parts to the questions example that starts with an "alphabet" (example "a" or "10 a") please extend the bounding box to cover the subparts as one question. 

Disregard the "Ans" boxes. Only output the questions in the final json.

If the image file has no questions, return an empty json object like {}

TOPICS:
Numbers up to 100
Addition and Subtraction
Multiplication and Division
Numbers up to 1000
Numbers up to 10 000
Numbers up to 100 000
Factors and Multiples
Four Operations
Numbers up to 10 million
Fraction of a Whole
Addition and Subtraction
Equivalent fractions
Addition and subtraction
Mixed Numbers and Improper Fractions
Fraction of a Set of Objects
Addition and Subtraction
Fraction and Division
Four Operations
Decimals up to 3 decimal places
Addition and Subtraction
Multiplication and Division
Four Operations
Money
Percentage
Ratio
Rate
Distance, Time and Speed
Algebra
Length
Time
Length, Mass and Volume
Area and Perimeter
2D Shapes
3D Shapes
Angles
Perpendicular and Parallel Lines
Triangle
Parallelogram, Rhombus and Trapezium
Special Quadrilaterals
Nets
Area of Triangle
Volume of Cube and Cuboid
Area and Circumference of Circle
Picture Graphs
Picture Graphs with Scales
Bar Graphs
Pie Charts
Average of a Set of Data
"""

def get_image(pdf_file, page_num):
    '''
    get_image - Gets and image from a pdf_file
    '''
    doc = pymupdf.open(pdf_file) # open a document
    pix = doc[page_num].get_pixmap()
    output = "test.png"
    temp_file = tempfile.TemporaryFile(dir="./temp", suffix=".png")
    print(temp_file.name)
    temp_file.close()
    pix.save(temp_file.name)
    return temp_file

class PdfImagerGenerator:
    '''
    PdfImagerGenerator
    '''
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.doc = pymupdf.open(pdf_file) # open a document
        #How many characters are in the length of the doc. Eg. 12= 2 characters, 100 = 3 characters.
        self.doc_length_str = len(str(len(self.doc))) 
        
    def save_image(self, filename, page_num):
        pixmap = self.doc[page_num].get_pixmap()
        pixmap.save(filename)

    def process_file(self, dir, prefix, suffix):
        for i,d in enumerate(self.doc):
            filename = prefix+str(i).zfill(self.doc_length_str)+suffix
            full_path = os.path.join(dir,filename)
            print(full_path)
            self.save_image(full_path, i)

    def generate_image_tempfile(self, dir, page_num):
        temp_file = tempfile.TemporaryFile(dir=dir, suffix=".png", delete=False)
        print(temp_file.name)
        temp_file.close()
        self.image_generator.save_image(temp_file.name, page_num)
        return temp_file.name
        
        return self.generate_with_image_file(temp_file.name)

class Gemini_Exam:
    def __init__(self, client):        
        self.client = client                
        
    def clean_json(self, output):
        lines = output.split("\n")
        clean_lines = [l for l in lines if l.startswith("```") is False]
        return "\n".join(clean_lines)        
    
    def generate_with_image_file(self, image_file_path):
        #Files
        files = [
            # Make the file available in local system working directory
            
            #client.files.upload(file="Screenshot 2025-03-24 111132.png"),
            self.client.files.upload(file=image_file_path),                
        ]
        
        model = "gemini-2.0-flash"
        
        #Content
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=files[0].uri,
                        mime_type=files[0].mime_type,
                    ),
                ],
            ),
        ]
        
        #Config
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=SYSTEM_PROMPT),
            ],
        )
        
        output = ""
        for chunk in self.client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            #print(chunk.text, end="")
            output = output + chunk.text
                    
        return json.loads(self.clean_json(output))
    
def create_directory_if_not_exists(directory_path):
  """
  Creates a directory if it does not exist.

  Args:
    directory_path: The path to the directory.
  """
  if not os.path.exists(directory_path):
    try:
      os.makedirs(directory_path)  # Use makedirs to create nested directories
      print(f"Directory '{directory_path}' created.")
    except OSError as e:
      print(f"Error creating directory '{directory_path}': {e}")
  else:
    print(f"Directory '{directory_path}' already exists.")


def process_images_dir(dir,vllm, skip=[]):
    files = glob.glob(os.path.join(dir,"*.png"))
    print(files)
    for f in files:
        page_num = extract_page_num(f)
        if page_num in skip:
            pass
            print("Skipping "+f)
        else:
            process_file(vllm, f)

def extract_page_num(filepath):
    path = Path(filepath)
    splits = path.name.split(".")[0].split("_")
    return int(splits[-1])

def process_file(vllm, f):
    output = vllm.generate_with_image_file(f)
    output_file = Path(f+".json")

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(output, f)




if __name__ == "__main__":
    
    

    '''
    file="2023-P6-Maths-Weighted Assessment 1-Raffles.pdf"

    results = []
    metadata = {
        "filename":file,

    }
    exam_parser = Gemini_Exam("2023-P6-Maths-Weighted Assessment 1-Raffles.pdf",client,temp_dir="./temp")
    exam_parser.num_pages()
    output = exam_parser.generate(1)
    r = {
        
    }
    results.append(output)
    #print()
    print(output)
    '''

    
    
    
    '''
    image_file = "./2024-P6-Maths-Prelim Exam-ACSJ/2024-P6-Maths-Prelim Exam-ACSJ3.png"
    
    output = exam_parser.generate_with_image_file(image_file)
    image_file_path = Path(image_file)
    print(image_file_path.name)
    print(output)
    output_file = Path(image_file+".json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(output, f)'
    '''

    pdf_filename = "2024-P6-Maths-Prelim Exam-Catholic High.pdf"
    image_gen = PdfImagerGenerator(pdf_filename)
    pdf_path = Path(pdf_filename)
    just_name = pdf_path.name.split(".")[0]
    pdf_images_path = os.path.join("./",just_name)
    create_directory_if_not_exists(pdf_images_path)

    image_gen.process_file(pdf_images_path,just_name +"_",".png")

'''
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"),)  
    exam_parser = Gemini_Exam(client)
    skips = [0,21,22]
    skips = skips + list(range(37,62))
    process_images_dir("./2024-P6-Maths-Prelim Exam-ACSP", exam_parser, skip=skips)
    #process_file(exam_parser, "./2024-P6-Maths-Prelim Exam-ACSJ/2024-P6-Maths-Prelim Exam-ACSJ_18.png")
'''