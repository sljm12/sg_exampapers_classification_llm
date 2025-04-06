import gradio as gr
import os
from exam_gemini import PdfImagerGenerator, create_directory_if_not_exists
from pathlib import Path

paper_root = "./papers"

def process_file(file_obj):
    if file_obj is None:
        return "Please upload a file."
    else:
        filename = file_obj.name
        file_size = os.path.getsize(filename)        
        
        image_gen = PdfImagerGenerator(filename)
        pdf_path = Path(filename)
        just_name = pdf_path.name.split(".")[0]
        pdf_images_path = os.path.join(paper_root, just_name)
        create_directory_if_not_exists(pdf_images_path)
        image_gen.process_file(pdf_images_path,just_name +"_",".png")

        return [f"File '{filename}' uploaded successfully. File size: {file_size} bytes.", papers_list_click(just_name)]

def refresh_papers_click():
    choices = [d for d in os.listdir(paper_root) if os.path.isdir(os.path.join(paper_root,d))]
    return gr.Dropdown(choices=choices, interactive=True)

def papers_list_click(a):
    path = os.path.join(paper_root, a)
    files = [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) and f.endswith(".png")]
    print(files)
    return files

with gr.Blocks() as demo:
    with gr.Tab("Upload"):
        file = gr.File()
        submit = gr.Button("Submit")
        status = gr.Text(label="Output")
        
        with gr.Row():
            selected = gr.Number()
            upload_skip = gr.Button("Skip>>")
            upload_back = gr.Button("Back")
        with gr.Row():
            upload_pages = gr.Gallery(label="Pages", scale=1, allow_preview=False)
            upload_skip = gr.Gallery(label="Skip", scale=1)

        def get_select_index(evt: gr.SelectData):
            return evt.index

        upload_pages.select(get_select_index, None, selected)
        submit.click(process_file,inputs=file, outputs=[status, upload_pages])
        #upload_skip.click(inputs=upload_pages, outputs=[upload_pages,upload_skip])
        
    with gr.Tab("Papers"):
        refresh_papers = gr.Button("Refresh")
        papers_list = gr.Dropdown(choices=['a','b'], interactive=True)        
        papers_gallery = gr.Gallery()

        refresh_papers.click(refresh_papers_click, outputs=papers_list)    
        papers_list.change(papers_list_click, inputs=papers_list, outputs = papers_gallery)

if __name__ == "__main__":
    demo.launch()