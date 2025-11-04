from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Whiteboard, WhiteboardAccess, StickyNote, Drawing
from .serializers import (
    WhiteboardSerializer, WhiteboardAccessSerializer,
    StickyNoteSerializer, DrawingSerializer
)


class IsWhiteboardOwnerOrHasAccess(permissions.BasePermission):
    """Custom permission to only allow owners or users with access to view/edit"""
    
    def has_object_permission(self, request, view, obj):
        # Owner has all permissions
        if isinstance(obj, Whiteboard):
            if obj.owner == request.user:
                return True
            # Check access rights
            access = WhiteboardAccess.objects.filter(
                whiteboard=obj, 
                user=request.user
            ).first()
            if access:
                if request.method in permissions.SAFE_METHODS:
                    return True  # View access is sufficient for GET
                return access.role in ['edit', 'admin']  # Edit or admin needed for modifications
        
        # For StickyNote and Drawing, check whiteboard access
        elif isinstance(obj, (StickyNote, Drawing)):
            return self.has_object_permission(request, view, obj.whiteboard)
        
        return False


class WhiteboardViewSet(viewsets.ModelViewSet):
    serializer_class = WhiteboardSerializer
    permission_classes = [permissions.IsAuthenticated, IsWhiteboardOwnerOrHasAccess]
    
    def get_queryset(self):
        # Return whiteboards owned by user or accessible to user
        user = self.request.user
        return Whiteboard.objects.filter(
            Q(owner=user) | Q(access_rights__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def grant_access(self, request, pk=None):
        """Grant access to a user for this whiteboard"""
        whiteboard = self.get_object()
        
        # Only owner or admin can grant access
        if whiteboard.owner != request.user:
            access = WhiteboardAccess.objects.filter(
                whiteboard=whiteboard,
                user=request.user,
                role='admin'
            ).first()
            if not access:
                return Response(
                    {'error': 'Only owner or admin can grant access'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        username = request.data.get('username')
        role = request.data.get('role', 'view')
        
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        access, created = WhiteboardAccess.objects.get_or_create(
            whiteboard=whiteboard,
            user=user,
            defaults={'role': role}
        )
        
        if not created:
            access.role = role
            access.save()
        
        serializer = WhiteboardAccessSerializer(access)
        return Response(serializer.data)


class StickyNoteViewSet(viewsets.ModelViewSet):
    serializer_class = StickyNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Get notes from whiteboards user has access to
        accessible_whiteboards = Whiteboard.objects.filter(
            Q(owner=user) | Q(access_rights__user=user)
        ).distinct()
        return StickyNote.objects.filter(whiteboard__in=accessible_whiteboards)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DrawingViewSet(viewsets.ModelViewSet):
    serializer_class = DrawingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Get drawings from whiteboards user has access to
        accessible_whiteboards = Whiteboard.objects.filter(
            Q(owner=user) | Q(access_rights__user=user)
        ).distinct()
        return Drawing.objects.filter(whiteboard__in=accessible_whiteboards)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

