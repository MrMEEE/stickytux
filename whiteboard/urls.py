from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'whiteboards', views.WhiteboardViewSet, basename='whiteboard')
router.register(r'sticky-notes', views.StickyNoteViewSet, basename='stickynote')
router.register(r'drawings', views.DrawingViewSet, basename='drawing')

urlpatterns = [
    path('', include(router.urls)),
]
