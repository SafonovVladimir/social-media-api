from rest_framework import serializers
from .models import Post, Hashtag, Comment


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("name", )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "created_at")
        read_only_fields = ("id", "post", "author", "created_at")


class CommentContentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Comment
        fields = ("author", "content")
        read_only_fields = ("author", "content")


class PostSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, read_only=True)
    comments = CommentContentSerializer(many=True, read_only=True)
    author = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "image",
            "created_at",
            "hashtags",
            "comments",
            "likes"
        )
        read_only_fields = ("id", "author", "created_at", "image", )
