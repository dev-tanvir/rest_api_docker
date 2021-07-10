from django.urls import path, include
from synthesize import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tag', views.TagViewSet)

app_name = 'synthesize'

urlpatterns = [
    path('', include(router.urls))
]



