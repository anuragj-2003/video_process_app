# video_process_app
This Django application lets users upload videos, extracts subtitles with `ccextractor`, and stores the results in AWS S3 and DynamoDB. Celery handles background processing. Users can search subtitles to find specific keywords and their corresponding time segments in the videos.
