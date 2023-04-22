from rest_framework import serializers
from .models import Post, Hashtag


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("name", )


class PostSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, read_only=True)
    author = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "image", "created_at", "hashtags")
        read_only_fields = ["id", "created_at"]
