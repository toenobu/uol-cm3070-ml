import logging
import json

import requests
import boto3
import os
import tempfile
from PIL import Image
import io
import numpy as np
import torch
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer
import faiss
from datasets import load_from_disk

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize global variables for reuse across Lambda invocations
model = None
processor = None
tokenizer = None
dataset = None
s3_client = None

programboy-cm3070-foobarfoobarfoobarml

def init_resources():
    global model, processor, tokenizer, dataset, s3_client

    # Initialize S3 client
    s3_client = boto3.client('s3')
    bucket_name = BUCKET_NAME

    # Create temp directory for downloads
    tmp_dir = tempfile.mkdtemp()

    logger.info(f"Temporary directory created at: {tmp_dir}")
    print(f"Temporary directory created at: {tmp_dir}")

    # Define file paths for dataset components
    dataset_dir = "dataset"
    index_dir = "index"

    # Dataset files to download
    ds_files = [
        f'{dataset_dir}/data-00000-of-00001.arrow',
        f'{dataset_dir}/dataset_info.json',
        f'{dataset_dir}/state.json'
    ]

    # FAISS index files to download
    faiss_files = [
        f'{index_dir}/embeddings.faiss',
        f'{index_dir}/image_embeddings.faiss'
    ]

    # Create local directories for downloads
    local_ds_dir = f"{tmp_dir}/{dataset_dir}"
    local_index_dir = f"{tmp_dir}/{index_dir}"
    os.makedirs(local_ds_dir, exist_ok=True)
    os.makedirs(local_index_dir, exist_ok=True)

    # Download dataset files from S3
    logger.info(f"Downloading dataset files from {bucket_name}")
    for file_path in ds_files:
        filename = os.path.basename(file_path)
        local_path = f"{local_ds_dir}/{filename}"
        logger.info(f"Downloading {file_path} to {local_path}")
        s3_client.download_file(bucket_name, file_path, local_path)

    # Download FAISS index files from S3
    logger.info(f"Downloading FAISS index files from {bucket_name}")
    for file_path in faiss_files:
        filename = os.path.basename(file_path)
        local_path = f"{local_index_dir}/{filename}"
        logger.info(f"Downloading {file_path} to {local_path}")
        s3_client.download_file(bucket_name, file_path, local_path)

    # Load the dataset and FAISS indexes
    dataset = load_from_disk(local_ds_dir)
    dataset.load_faiss_index('embeddings', f"{local_index_dir}/embeddings.faiss")
    dataset.load_faiss_index('image_embeddings', f"{local_index_dir}/image_embeddings.faiss")

    model_dir = f"{tmp_dir}/model"
    processor_dir = f"{tmp_dir}/processor"
    tokenizer_dir = f"{tmp_dir}/tokenizer"

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(processor_dir, exist_ok=True)
    os.makedirs(tokenizer_dir, exist_ok=True)

    device = torch.device('cuda' if torch.cuda.is_available() else "cpu")
    model = AutoModel.from_pretrained("openai/clip-vit-base-patch16", cache_dir=model_dir).to(device)
    processor = AutoImageProcessor.from_pretrained("openai/clip-vit-base-patch16", cache_dir=processor_dir)
    tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch16", cache_dir=tokenizer_dir)

    logger.info("Resources initialized successfully")
    return dataset

def handler(event, context):
    """
    AWS Lambda function handler.

    Parameters:
    event (dict): Event data from the Lambda trigger
    context (object): Runtime information

    Returns:
    dict: Response with statusCode and body
    """
    global model, processor, tokenizer, dataset, s3_client

    # Initialize resources if not already done
    if model is None or dataset is None:
        dataset = init_resources()

    bucket, key = extract_s3_info(event)

    if not bucket or not key:
        logger.error("Failed to extract bucket and key from S3 event")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid S3 event format"})
        }

    image = get_image(bucket, key, s3_client)

    # Generate image embedding
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_embedding = model.get_image_features(**inputs).cpu().numpy()[0]

    # Search for similar items using image_embeddings index
    scores, retrieved_examples = dataset.get_nearest_examples('image_embeddings', image_embedding, k=5)

    # Process results
    logger.info(f"retrieved_examples: {retrieved_examples}")
    results = []
    for i, (score, label) in enumerate(zip(scores, retrieved_examples['label'])):
        results.append({
            'score': float(score),  # Convert numpy float to Python float for JSON serialization
            'label': get_disease_name(label),
            'rank': i + 1
        })

    disease_counts = {}
    for result in results:
        disease = result['label']
        if disease in disease_counts:
            disease_counts[disease] += 1
        else:
            disease_counts[disease] = 1

    most_likely_disease = max(disease_counts.items(), key=lambda x: x[1])[0]
    confidence_score = disease_counts[most_likely_disease] / len(results)

    body_data = {
        'most_likely_disease': most_likely_disease,
        's3_image_path': key,
        'score': confidence_score,
        'results': results
    }

    body = json.dumps(body_data)

    # Send the data to the endpoint specified in the environment variable
    api_endpoint = os.environ.get('API_ENDPOINT')
    x_tomato_header_value = os.environ.get('X_TOMATO_HEADER_VALUE')

    if api_endpoint:
        try:
            response = requests.post(
                api_endpoint,
                json=body_data,
                headers={'Content-Type': 'application/json', 'x-tomato': x_tomato_header_value}
            )
            logger.info(f"Data sent to API endpoint. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending data to API endpoint: {str(e)}")
    else:
        logger.warning("API_ENDPOINT environment variable not set. Data not sent to any endpoint.")


    # Return a response suitable for API Gateway
    response = {
        "statusCode": 200,
        "body": body
    }

    logger.info(f"result: {body}")

    return response

def extract_s3_info(event):

    # For S3 triggered events
    s3_event = event.get('Records', [{}])[0].get('s3', {})
    bucket = s3_event.get('bucket', {}).get('name')
    key = s3_event.get('object', {}).get('key')

    return bucket, key

def get_image(bucket, key, s3_client):
    """
    Retrieve and load an image from S3.

    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key
        s3_client: Boto3 S3 client

    Returns:
        PIL.Image: Loaded image object
    """
    logger.info(f"Processing file {key} from bucket {bucket}")

    try:
        # Use in-memory processing to avoid file I/O
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        logger.error(f"Error loading image from S3: {str(e)}")
        raise



# Disease mapping dictionary
DISEASE_MAPPING = {
    0: "Bacterial spot",
    1: "Early blight",
    2: "Late blight",
    3: "Leaf Mold",
    4: "Septoria leaf spot",
    5: "Tomato Yellow Leaf Curl Virus",
    6: "Tomato mosaic virus",
    7: "healthy"
}

def get_disease_name(disease_key):
    """
    Convert a disease key to its corresponding name.

    Args:
        disease_key : The disease identifier

    Returns:
        str: The name of the disease, or "Unknown" if not found
    """

    # Return the disease name or "Unknown" if not in mapping
    return DISEASE_MAPPING.get(disease_key, "Unknown")

if __name__ == "__main__":
    # For local testing
    test_event = {}
    test_context = None
    result = handler(test_event, test_context)
    print(result)
