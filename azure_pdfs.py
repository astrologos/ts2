# %%
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.storage.blob import BlobServiceClient
import PyPDF2
from tqdm import tqdm
from time import sleep


# %%
# Constants for the Azure Document Intelligence API and Azure Blob Storage
AzureKeys = {
    "DocumentIntelligence": {
        "KEY_1" : r"a9b43ebbe45b43b6a7f31b8aaf794ebd",
        "KEY_2" : r"4035977e991d4f978f1c0cb99bef3dc5",
        "AZURE_ENDPOINT" : r"https://termsheets.cognitiveservices.azure.com/",
        "AZURE_REGION" : r"eastus"
    },
    "BlobStorage": {
        "CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=ts2;AccountKey=UL/fYklCwDLpxnKYLvLg84nUQrJRo4nuwxShhOT8gC3ZtFymf7czeywf0UzFTNB1dwUV++ptugKH+AStesxhFA==;EndpointSuffix=core.windows.net",
        "CONTAINER_NAME": "ts2"
    }
}

# %%
# Connect to the Azure Document Intelligence API
def doc_client(AzureKeys):
    # Set the values for the Azure Document Intelligence API
    key = AzureKeys["DocumentIntelligence"]["KEY_1"]
    endpoint = AzureKeys["DocumentIntelligence"]["AZURE_ENDPOINT"]
    region = AzureKeys["DocumentIntelligence"]["AZURE_REGION"]

    # Create a client
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    return client

# %%
# Connect to Azure Blob Storage
def blob_client(AzureKeys):
    # Set the values for Azure Blob Storage
    connection_string = AzureKeys["BlobStorage"]["CONNECTION_STRING"]
    container_name = AzureKeys["BlobStorage"]["CONTAINER_NAME"]

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    return container_client

# %%
doc_client = doc_client(AzureKeys)
blob_client = blob_client(AzureKeys)


# %%
# Upload document to blob storage
def upload_blob(blob_client, file_path, blob_name):
    """
    Uploads a document to blob storage.

    Parameters:
    blob_client (BlobServiceClient): The blob service client.
    file_path (str): The path to the document to upload.
    blob_name (str): The name of the blob to create.

    Returns:
    A list of all files not uploaded.
    """

    with open(file_path, "rb") as data:
        blob_client.upload_blob(name=blob_name, data=data)
        
        # Test if the blob was uploaded
        blob = blob_client.get_blob_client(blob_name)

        if(blob.exists()):  
            print("Blob uploaded successfully.")
        else:
            print("Blob not uploaded successfully.")
            return blob_name


# Upload multiple documents to blob storage
    """
    Uploads multiple documents to blob storage.

    Parameters:
    blob_client (BlobServiceClient): The blob service client.
    file_paths (list): A list of paths to the documents to upload.
    blob_names (list): A list of the names of the blobs to create.
    """
def upload_multiple_blobs(blob_client, file_paths, blob_names):
    for file_path, blob_name in zip(file_paths, blob_names):
        upload_blob(blob_client, file_path, blob_name)




def download_blob(blob_client, blob_name, file_path):
    """
    Downloads a document from blob storage.
        
    Parameters:
    blob_client (BlobServiceClient): The blob service client.
    blob_name (str): The name of the blob to download.
    file_path (str): The path to save the downloaded document.
    
    Returns:
    A list of all files not downloaded.      
        
    """

    with open(file_path, "wb") as data:
        blob_client.download_blob(blob_name).readinto(data)

# %%
# Get relative paths from a given directory
def get_files(directory, extension):
    """
    Get a list of files in a directory with a given extension.

    Parameters:
    directory (str): The directory to search.
    extension (str): The file extension to search for.

    Returns:
    A list of file paths.
    """

    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extension):
                files.append(os.path.relpath(os.path.join(root, filename), directory))
    return files


data_path = "./term sheets/source"
save_dir = "./term sheets/split"
files = get_files(data_path, ".pdf")
files 

file_paths = [data_path + "/" + file for file in files]

# %%
file_paths

# %%
# Function to open a PDF file and save each page as a separate PDF locally
def split_pdf_file(load_file_path, save_directory_path):
    """
    Splits a PDF file into separate pages and saves each page as a separate PDF file.
    
    Parameters:
    file_path (str): The path to the PDF file to split.
    """

    # Get the file name from the file path
    file_name = load_file_path.split(r"/")[-1].split(".")[0]

    # If save directory path does not exist, create it
    if not os.path.exists(save_directory_path):
        os.makedirs(save_directory_path)
    
    # Open the PDF file
    pdf_file = open(load_file_path, "rb")
    pdf = PyPDF2.PdfReader(pdf_file)
    
    # Save each page as a separate PDF file
    for page_num in range(len(pdf.pages)):
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(pdf.pages[page_num])
        output_filename = f"{save_directory_path}/{file_name}_page_{page_num+1}.pdf"
        with open(output_filename, "wb") as output_pdf:
            # Write to output directory
            pdf_writer.write(output_pdf)
    
        # Close the output PDF file
        output_pdf.close()

        # Close the PDF writer
        pdf_writer.close()
        
        # Sleep for 0.5 second to avoid throttling
        sleep(0.5)

    # Close the PDF file
    pdf_file.close()

# %%
save_dir

# %%
split_pdf_file(file_paths[0], save_dir)

# %%
def split_pdf_files(file_paths: list, output_directory: str):
    # Split each PDF file
    for file in tqdm(file_paths, desc="Splitting PDF files...", unit="file"):
        sleep(0.5)
        split_pdf_file(file, output_directory)

split_pdf_files(file_paths, save_dir)

# %%
# blob_list = list(blob_client.list_blobs())

# if len(blob_list)==0:
#     print("No blobs found in the container.")
# else: # Print all blobs
#     for blob in blob_list:
#         print(blob.name)

# %%
# # Download the blob
# blob_data = blob_client.download_blob(blob)
# blob_data = blob_data.readall()

# # Analyze the document
# doc = AnalyzeDocumentRequest(file=blob_data, content_type="application/pdf")
# result = doc_client.begin_analyze_document(doc).result()



