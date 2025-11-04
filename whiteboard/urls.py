from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views
from . import user_views

router = DefaultRouter()
router.register(r'whiteboards', views.WhiteboardViewSet, basename='whiteboard')
router.register(r'sticky-notes', views.StickyNoteViewSet, basename='stickynote')
router.register(r'sticky-note-images', views.StickyNoteImageViewSet, basename='stickynoteimage')
router.register(r'drawings', views.DrawingViewSet, basename='drawing')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', auth_views.login_view, name='login'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/csrf/', auth_views.csrf_token_view, name='csrf'),
    path('users/search/', user_views.search_users, name='search_users'),
]
