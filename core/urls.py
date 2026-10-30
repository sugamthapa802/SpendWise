from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterView,MeView,CategoryViewset
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


# viewsets specific router urls :
router=DefaultRouter()
router.register("categories",CategoryViewset,basename="category")

urlpatterns = [
    path('auth/register/',RegisterView.as_view(),name="register"),
    path('auth/login/',TokenObtainPairView.as_view(),name="login"),
    path('token/refresh/',TokenRefreshView.as_view(),name="refresh_token"),
    path('me/',MeView.as_view(),name="me"),

]

urlpatterns+=router.urls