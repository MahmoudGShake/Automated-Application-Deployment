from django.urls import path,include,re_path
from .views import *
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("articles",ArticleView)
router.register("category",CategoryView)
urlpatterns = [
    path("",include(router.urls)),
    ]

