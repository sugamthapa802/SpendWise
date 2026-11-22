from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterView,MeView,CategoryViewset, TransactionViewset, BudgetViewset,SummaryView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework.schemas import get_schema_view
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# viewsets specific router urls :
router=DefaultRouter()
router.register("categories",CategoryViewset,basename="category")
router.register("transactions",TransactionViewset,basename="transaction")
router.register("budget",BudgetViewset,basename="budget")


# schema_view = get_schema_view(
#     title= "SpendWise API",
#     description="Lets the user create different categories as expense or income, can create transactions and budget within the" \
#     "available categories.",
#     version="1.0"

# )

urlpatterns = [
    path('auth/register/',RegisterView.as_view(),name="register"),
    path('auth/login/',TokenObtainPairView.as_view(),name="login"),
    path('token/refresh/',TokenRefreshView.as_view(),name="refresh_token"),
    path('me/',MeView.as_view(),name="me"),
    path('summary/',SummaryView.as_view(),name="summary"),
    # path('schema/',schema_view,name="schema_view" ),
    path('schema/',SpectacularAPIView.as_view(), name= "schema"),
    path('docs/',SpectacularSwaggerView.as_view(url_name='schema'), name= "swagger-ui"),
    path('redoc/',SpectacularRedocView.as_view(url_name='schema'), name= "redoc"),

]

urlpatterns+=router.urls