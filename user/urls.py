from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView
)
from rest_framework import routers

from user.views import (
    CreateUserView,
    ManageUserView,
    UserProfileViewSet,
    toggle_following_user,
    UserFollowersViewSet,
    UserFollowingsViewSet,
)

app_name = "user"

router = routers.SimpleRouter()
router.register("profile", UserProfileViewSet)
router.register("following", UserFollowingsViewSet)
router.register("followers", UserFollowersViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="manage"),
]
