import os
import boto3
import gradio as gr
from botocore.exceptions import ClientError
from modules import scripts, script_callbacks
from modules.shared import opts, cmd_opts
from subprocess import getoutput

list_dirs = [
    os.path.realpath(opts.outdir_samples or opts.outdir_txt2img_samples),
    os.path.realpath(opts.outdir_samples or opts.outdir_img2img_samples),
    os.path.realpath(opts.outdir_samples or opts.outdir_extras_samples),
    os.path.realpath(opts.outdir_grids or opts.outdir_txt2img_grids),
    os.path.realpath(opts.outdir_grids or opts.outdir_img2img_grids)
]

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

def get_s3_client():
    return boto3.client('s3', 
                    aws_access_key_id=os.getenv('aws_access_key_id'), 
                    aws_secret_access_key=os.getenv('aws_secret_access_key'), 
                    region_name=os.getenv('aws_region', 'ap-southeast-1')
                )

def upload_folder():
    """Upload a folder to an S3 bucket

    :param folder_name: Folder to upload
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = get_s3_client()
    try:
        for folder_name in list_dirs:
            if os.path.exists(folder_name):
                files = getListOfFiles(folder_name)
                for elem in files:
                    print('Uploading ' + elem)
                    s3_client.upload_file(elem, os.getenv('aws_s3_bucket'), elem)
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
                    out_folder = gr.Textbox(show_label=False)
                    btn_push_folder = gr.Button("Push To S3")
            btn_push_folder.click(upload_folder, inputs=[], outputs=out_folder)
    return (pushToX, "Push To X", "pushToX"),
script_callbacks.on_ui_tabs(on_ui_tabs)