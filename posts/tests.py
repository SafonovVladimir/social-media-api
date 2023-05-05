from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Hashtag, Comment
from posts.serializers import PostSerializer


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PostTests(APITestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_posts(self):
        response = self.client.get(reverse("post:post-feed"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hashtag_model(self):
        hashtag = Hashtag.objects.create(name="test")
        self.assertEqual(str(hashtag), hashtag.name)

    def test_comment_model(self):
        post = Post.objects.create(
            author=self.user,
            content="This is test post"
        )
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            content="Comment for testing"
        )
        self.assertEqual(str(comment), comment.author.email)

    def test_post_serializer(self):
        post = Post.objects.create(author=self.user)
        serializer = PostSerializer(post)
        expected_fields = ([
            "id",
            "author",
            "content",
            "image",
            "created_at",
            "hashtags",
            "comments",
            "likes"
        ])
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))
