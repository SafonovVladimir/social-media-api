from typing import Type

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserProfileListSerializer,
    UserProfileDetailSerializer, UserListSerializer,
)
from user.models import UserProfile


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> Request:
        return self.request.user


class UserProfileViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return UserProfileListSerializer

        if self.action == "retrieve":
            return UserProfileDetailSerializer

        # if self.action == "upload_image":
        #     return MovieImageSerializer

        return UserProfileListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserFollowViewSet(mixins.ListModelMixin, viewsets.GenericViewSet,):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)


class UserFollowersViewSet(UserFollowViewSet):
    def get_queryset(self):
        my_user = get_user_model().objects.get(id=self.request.user.id)
        return my_user.profile.followers.all()


class UserFollowingsViewSet(UserFollowViewSet):
    def get_queryset(self):
        return self.queryset.filter(profile__followers=self.request.user.id)


@api_view(["GET"])
def toggle_following_user(request, pk):
    user = get_user_model().objects.get(id=request.user.id)
    following = get_user_model().objects.get(id=pk)

    if user in following.profile.followers.all():
        following.profile.followers.remove(user.id)
    else:
        following.profile.followers.add(user.id)

    return HttpResponse(status=status.HTTP_200_OK)
