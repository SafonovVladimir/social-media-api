from typing import Type

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserProfileListSerializer,
    UserProfileDetailSerializer,
    UserListSerializer,
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
    queryset = (UserProfile.objects
                .prefetch_related("followers")
                .select_related("user"))
    serializer_class = UserProfileListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        """Retrieve the users profiles with filters"""
        phone = self.request.query_params.get("phone")
        birthday = self.request.query_params.get("birthday")

        queryset = self.queryset

        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        if birthday:
            queryset = queryset.filter(birthday__year=birthday)

        return queryset.distinct()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return UserProfileListSerializer

        if self.action == "retrieve":
            return UserProfileDetailSerializer

        return UserProfileListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "phone",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by phone or number (ex. ?phone=123)"
            ),
            OpenApiParameter(
                "birthday",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by birthday or year (ex. ?birthday=2000)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs) -> list:
        return super().list(request, *args, **kwargs)


class UserFollowViewSet(mixins.ListModelMixin, viewsets.GenericViewSet,):
    queryset = get_user_model().objects.select_related("profile")
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)


class UserFollowersViewSet(UserFollowViewSet):
    def get_queryset(self):
        user = self.queryset.get(id=self.request.user.id)
        return user.profile.followers


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

    return Response(status=status.HTTP_200_OK)
