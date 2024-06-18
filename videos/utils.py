# #videos/utils.py
import os
import subprocess
import boto3
from pathlib import Path
import logging
from django.conf import settings
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger(__name__)

def save_video_locally(video):
    video_path = os.path.join(settings.MEDIA_ROOT, video.name)
    with open(video_path, 'wb+') as destination:
        for chunk in video.chunks():
            destination.write(chunk)
    return video_path

def extract_subtitles(video_path):
    try:
        subtitles_path = os.path.splitext(video_path)[0] + '.srt'
        if not os.path.exists(subtitles_path):
            ccextractor_path = r'C:\Program Files (x86)\CCExtractor\ccextractorwinfull.exe'
            subprocess.run([ccextractor_path, video_path, '-o', subtitles_path], check=True)
        return subtitles_path
    except Exception as e:
        logger.error(f"Failed to extract subtitles from {video_path}: {str(e)}")
        raise

def upload_to_s3(file_path):
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION_NAME)
        s3.upload_file(file_path, settings.AWS_S3_BUCKET_NAME, os.path.basename(file_path))
        logger.info(f"Uploaded {file_path} to S3 bucket {settings.AWS_S3_BUCKET_NAME}")
    except Exception as e:
        logger.error(f"Failed to upload {file_path} to S3: {str(e)}")
        raise


def save_subtitles_to_dynamodb(video_id, subtitles_path):
    try:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                  region_name=settings.AWS_REGION_NAME)
        table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
        
        with open(subtitles_path, 'r') as f:
            subtitles = f.read()
        
        for index, line in enumerate(subtitles.split('\n\n')):
            if line.strip():
                timestamp = str(index)
                item = {
                    'VideoID': video_id,
                    'Timestamp': timestamp,
                    'Content': line.strip()
                }
                response = table.put_item(Item=item)
                logger.info(f"Inserted item: {item}")
                logger.info(f"DynamoDB response: {response}")
        
        logger.info(f"Successfully saved subtitles from {subtitles_path} to DynamoDB table {settings.DYNAMODB_TABLE_NAME}")
    
    except Exception as e:
        logger.error(f"Failed to save subtitles from {subtitles_path} to DynamoDB: {str(e)}")
        raise


def view_items_in_dynamodb():
    try:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                  region_name=settings.AWS_REGION_NAME)
        table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
        response = table.scan()
        items = response['Items']
        for item in items:
            print(item)
    except Exception as e:
        print(f"Failed to view items in DynamoDB: {str(e)}")

def search_subtitles_in_dynamodb(query):
    try:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                  region_name=settings.AWS_REGION_NAME)
        table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
        response = table.scan(
            FilterExpression=Attr('Content').contains(query)
        )
        return [item['Content'] for item in response['Items']]
    except Exception as e:
        logger.error(f"Failed to search subtitles in DynamoDB: {str(e)}")
        raise

def process_video(video_path):
    output_path = video_path.replace('.mp4', '_processed.mp4')
    try:
        subprocess.run(['ffmpeg', '-i', video_path, '-ss', '00:00:10', '-to', '00:00:20', '-c', 'copy', output_path], check=True)
        logger.info(f"Processed video saved to {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing video: {str(e)}")
        raise RuntimeError(f"Error processing video: {str(e)}")
