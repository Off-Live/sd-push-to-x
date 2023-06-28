import os
import boto3
import numpy as np
import gradio as gr
# from huggingface_hub import model_info, create_repo, create_branch, upload_folder, upload_file
# from huggingface_hub.utils import RepositoryNotFoundError, RevisionNotFoundError
from botocore.exceptions import ClientError
from modules import scripts, script_callbacks
from subprocess import getoutput

def run(command):
    out = getoutput(f"{command}")
    return out

# create a list of file and sub directories 
# names in the given directory 
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

def upload_folder(folder_name):
    """Upload a folder to an S3 bucket

    :param folder_name: Folder to upload
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        files = getListOfFiles(folder_name)
        for elem in files:
            print('Uploading ' + elem)
            s3_client.upload_file(elem, '10k-asset', elem)
    except ClientError as e:
        return "Failed pushing to S3"
    return "Done pushing to S3"


def on_ui_tabs():     
    with gr.Blocks() as pushToX:
        gr.Markdown(
        """
        ### Push Outputs to S3
        """)
        with gr.Group():
            with gr.Box():
                with gr.Row().style(equal_height=True):
                    text_folder_from = gr.Textbox(show_label=False, max_lines=1, placeholder="folder_from")
                    out_folder = gr.Textbox(show_label=False)
                    btn_push_folder = gr.Button("Push To S3")
            btn_push_folder.click(upload_folder, inputs=[text_folder_from], outputs=out_folder)
    return (pushToX, "Push To X", "pushToX"),
script_callbacks.on_ui_tabs(on_ui_tabs)