from celery import shared_task
from django.utils import timezone
from .models import Post


@shared_task
def create_post(title, content):
    Post.objects.create(
        title=title,
        content=content,
        published_at=timezone.now()
    )
