from django.urls import path

from .views import (
    CreatePostView,
    PostListView,
    PostViewSet,
    like_post, LikedPostList,
)

app_name = "post"

urlpatterns = [
    path("feed/", PostListView.as_view(), name="post-feed"),
    path(
        "my-posts/",
        PostViewSet.as_view({"get": "user_posts"}),
        name="my_posts"
    ),
    path("create/", CreatePostView.as_view(), name="post-create"),
    path("<int:pk>/like/", like_post, name="like-post"),
    path("liked/", LikedPostList.as_view(), name="liked-post-list"),
]
