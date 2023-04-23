from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Post, Comment
from .tasks import create_post
from .serializers import PostSerializer, CommentSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.select_related("hashtags")

    def get_queryset(self) -> QuerySet:
        """Retrieve the posts with filters"""
        followed_users = self.request.user.profile.followers.all()
        queryset = Post.objects.filter(author__in=followed_users)
        hashtags = self.request.query_params.get("hashtags")

        if hashtags:
            queryset = queryset.filter(hashtags__name__icontains=hashtags)

        return queryset

    # only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "hashtags",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by hashtags or chars (ex. ?hashtags=files)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs) -> list:
        return super().list(request, *args, **kwargs)


class CreatePostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(
            author__in=user.profile.followers.all()
        ) | Post.objects.filter(author=user)

    @action(detail=False, methods=["get"])
    def user_posts(self, request):
        queryset = self.get_queryset().filter(author=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikedPostList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(likes=user)


@api_view(["GET"])
def schedule_post(request, post_id: int) -> Response:
    print(request.data)
    print(post_id)
    try:
        post = Post.objects.get(id=post_id)
        serializer = PostSerializer(post)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    publish_time = request.data.get("publish_time")
    print(publish_time)

    if not publish_time:
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        publish_time = timezone.make_aware(publish_time)
    except ValueError:
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        post.schedule_publish(publish_time)
        create_post.apply_async(
            args=[post.title, post.content],
            eta=publish_time
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    except ValidationError:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return Response(status=status.HTTP_200_OK)
