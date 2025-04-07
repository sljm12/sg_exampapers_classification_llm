import gradio as gr
import os
from exam_gemini import PdfImagerGenerator, create_directory_if_not_exists
from pathlib import Path

paper_root = "./papers"

class GradioAppState:
    def __init__(self):
        self.current_upload_dir=None
        self.paper_root = paper_root

    def get_paper_dir(self, paper_name):
        return os.path.join(self.paper_root, paper_name)

appState = GradioAppState()

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

        appState.current_upload_dir = pdf_images_path

        image_gen.process_file(pdf_images_path,just_name +"_",".png")

        return [f"File '{filename}' uploaded successfully. File size: {file_size} bytes.", papers_list_click(just_name)]

def refresh_papers_click():
    choices = [d for d in os.listdir(paper_root) if os.path.isdir(os.path.join(paper_root,d))]
    return gr.Dropdown(choices=choices, interactive=True)

def papers_list_click(a):
    path = os.path.join(paper_root, a)
    files = [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) and f.endswith(".png")]
    #print(files)
    return files


def convert_gallery_dir_paper_root(appState, gallery_input):
    if gallery_input is None:
        return []
    else:
        inputs = [i[0] for i in gallery_input]        

        return [os.path.join(appState.current_upload_dir, os.path.basename(i)) for i in inputs]


with gr.Blocks() as demo:
    
    with gr.Tab("Upload"):
        file = gr.File()
        submit = gr.Button("Submit")
        status = gr.Text(label="Output")
        
        with gr.Row():
            upload_pages_selected = gr.Number()
            upload_skip_btn = gr.Button("Skip>>")
            upload_back_btn = gr.Button("Back")
            call_llm = gr.Button("Call LLM")
            upload_skip_selected = gr.Number()
        with gr.Row():
            upload_pages_gallery = gr.Gallery(label="Pages", scale=1, allow_preview=False)
            upload_skip_gallery = gr.Gallery(label="Skip", scale=1, allow_preview=False)

        def get_select_index(evt: gr.SelectData):
            return evt.index
        
        def upload_skip_click(input_gallery, selected, output_gallery):
            converted_upload = convert_gallery_dir_paper_root(appState, input_gallery)
            converted_skip = convert_gallery_dir_paper_root(appState, output_gallery)

            print("Input Gallery ", converted_upload)
            selected_page = converted_upload[selected]
            print("Selected Page ",selected_page)            
            print("Output Gallery ", converted_skip)

            output = []
            if output_gallery is None:
                output = [selected_page]
            else:
                converted_skip.append(selected_page)
                output = converted_skip
            print("Output ",output)

            converted_upload.remove(selected_page)
            input = converted_upload
            return [input, output]
            


        upload_pages_gallery.select(get_select_index, None, upload_pages_selected)
        upload_skip_gallery.select(get_select_index, None, upload_skip_selected)
        submit.click(process_file,inputs=file, outputs=[status, upload_pages_gallery])
        upload_skip_btn.click(upload_skip_click, 
                              inputs=[upload_pages_gallery,upload_pages_selected, upload_skip_gallery], 
                              outputs=[upload_pages_gallery, upload_skip_gallery])
        '''
        upload_back_btn.click(upload_skip_click, 
                              inputs=[upload_pages_gallery,upload_pages_selected, upload_skip_gallery], 
                              outputs=[upload_pages_gallery, upload_skip_gallery])
        '''
    with gr.Tab("Papers"):
        refresh_papers = gr.Button("Refresh")
        papers_list = gr.Dropdown(choices=['a','b'], interactive=True)        
        papers_gallery = gr.Gallery()

        refresh_papers.click(refresh_papers_click, outputs=papers_list)    
        papers_list.change(papers_list_click, inputs=papers_list, outputs = papers_gallery)

if __name__ == "__main__":
    demo.launch()