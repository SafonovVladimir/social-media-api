from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Post
from .serializers import PostSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.select_related("hashtags")

    def get_queryset(self):
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
