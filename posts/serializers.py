from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'created_at', 'hashtags']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        post = Post(author=self.context['request'].user, **validated_data)
        post.save()
        return post