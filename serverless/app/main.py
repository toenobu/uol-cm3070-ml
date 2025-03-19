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

BUCKET_NAME = 'programboy-sagemaker-example'

def init_resources():
    global model, processor, tokenizer, dataset, s3_client

    # Initialize S3 client
    s3_client = boto3.client('s3')
    bucket_name = BUCKET_NAME

    # Create temp directory for downloads
    tmp_dir = tempfile.mkdtemp()

    logger.info(f"Temporary directory created at: {tmp_dir}")
    print(f"Temporary directory created at: {tmp_dir}")

    ds_files = [
        'ds/data-00000-of-00001.arrow',
        'ds/dataset_info.json',
        'ds/state.json'
    ]

    # Download FAISS indexes from S3
    faiss_files = [
        'index/embeddings.faiss',
        'index/image_embeddings.faiss'
    ]

    # Download dataset and embeddings using S3 client
    # Create directories if they don't exist
    ds_dir = f"{tmp_dir}/ds"
    indexes_dir = f"{tmp_dir}/index"
    os.makedirs(ds_dir, exist_ok=True)
    os.makedirs(indexes_dir, exist_ok=True)

    # List and download all objects with the dataset prefix
    for ds_file in ds_files:
        s3_key = f"example/{ds_file}"
        local_path = f"{ds_dir}/{os.path.basename(ds_file)}"
        s3_client.download_file(bucket_name, s3_key, local_path)

    # Download FAISS index files with specified prefix
    for faiss_file in faiss_files:
        s3_key = f"example/{faiss_file}"
        local_path = f"{indexes_dir}/{os.path.basename(faiss_file)}"
        s3_client.download_file(bucket_name, s3_key, local_path)

    # Load the dataset and FAISS indexes
    dataset = load_from_disk(ds_dir)
    dataset.load_faiss_index('embeddings', f"{indexes_dir}/embeddings.faiss")
    dataset.load_faiss_index('image_embeddings', f"{indexes_dir}/image_embeddings.faiss")

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
    for i, (score, image_description) in enumerate(zip(scores, retrieved_examples['image_description'])):
        results.append({
            'score': float(score),  # Convert numpy float to Python float for JSON serialization
            'label': image_description,
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

    body = json.dumps({
                'most_likely_disease': most_likely_disease,
                'confidence': confidence_score,
                'results': results
            })

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

if __name__ == "__main__":
    # For local testing
    test_event = {}
    test_context = None
    result = handler(test_event, test_context)
    print(result)
