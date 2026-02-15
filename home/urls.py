from django.urls import path
from .views import HomePage, ProductDetail

app_name = "home"

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('category/<slug:category_slug>/', HomePage.as_view(), name='category_filter'),
    path('<slug:slug>/', ProductDetail.as_view(), name='product_detail'),
]