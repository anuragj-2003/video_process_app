import logging
import os
import uuid
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import VideoUploadForm
from .tasks import process_video_task
from .utils import save_video_locally, extract_subtitles, upload_to_s3, save_subtitles_to_dynamodb, search_subtitles_in_dynamodb
from django.http import HttpResponseServerError

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'videos/index.html')

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                video = request.FILES['video']
                video_path = save_video_locally(video)
                subtitles_path = extract_subtitles(video_path)
                upload_to_s3(video_path)
                video_id = str(uuid.uuid4())
                save_subtitles_to_dynamodb(video_id, subtitles_path)
                process_video_task.delay(video_path)
                return redirect('upload_success')
            except Exception as e:
                logger.error(f"Error uploading video: {str(e)}")
                return redirect('error')
    else:
        form = VideoUploadForm()
    return render(request, 'videos/upload.html', {'form': form})



def upload_success(request):
    return render(request, 'videos/success.html')

def search_videos(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = search_subtitles_in_dynamodb(query)
    
    return render(request, 'videos/search.html', {'results': results, 'query': query})

def error(request):
    return render(request, 'videos/error.html')

def handler404(request, exception):
    return render(request, 'videos/not_found.html', status=404)
