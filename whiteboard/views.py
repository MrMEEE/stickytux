from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Max
from django.contrib.auth.models import User
from .models import Whiteboard, WhiteboardAccess, StickyNote, StickyNoteImage, Drawing, CustomColor, WhiteboardViewSettings
from .serializers import (
    WhiteboardSerializer, WhiteboardAccessSerializer,
    StickyNoteSerializer, StickyNoteImageSerializer, DrawingSerializer, CustomColorSerializer, WhiteboardViewSettingsSerializer
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
        
        # For StickyNoteImage, check sticky note's whiteboard access
        elif isinstance(obj, StickyNoteImage):
            return self.has_object_permission(request, view, obj.sticky_note.whiteboard)
        
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
    
    @action(detail=True, methods=['post'])
    def remove_access(self, request, pk=None):
        """Remove access for a user from this whiteboard"""
        whiteboard = self.get_object()
        
        # Only owner or admin can remove access
        if whiteboard.owner != request.user:
            access = WhiteboardAccess.objects.filter(
                whiteboard=whiteboard,
                user=request.user,
                role='admin'
            ).first()
            if not access:
                return Response(
                    {'error': 'Only owner or admin can remove access'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        username = request.data.get('username')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Cannot remove access from owner
        if user == whiteboard.owner:
            return Response(
                {'error': 'Cannot remove access from owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        WhiteboardAccess.objects.filter(
            whiteboard=whiteboard,
            user=user
        ).delete()
        
        return Response({'message': 'Access removed successfully'})


class StickyNoteViewSet(viewsets.ModelViewSet):
    serializer_class = StickyNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsWhiteboardOwnerOrHasAccess]
    
    def get_queryset(self):
        user = self.request.user
        # Get notes from whiteboards user has access to
        accessible_whiteboards = Whiteboard.objects.filter(
            Q(owner=user) | Q(access_rights__user=user)
        ).distinct()
        return StickyNote.objects.filter(whiteboard__in=accessible_whiteboards)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """Add an image to this sticky note"""
        note = self.get_object()
        
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the current max order
        max_order = note.images.aggregate(Max('order'))['order__max'] or -1
        
        image = StickyNoteImage.objects.create(
            sticky_note=note,
            image=image_file,
            order=max_order + 1
        )
        
        serializer = StickyNoteImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StickyNoteImageViewSet(viewsets.ModelViewSet):
    serializer_class = StickyNoteImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsWhiteboardOwnerOrHasAccess]
    
    def get_queryset(self):
        user = self.request.user
        # Get images from notes on whiteboards user has access to
        accessible_whiteboards = Whiteboard.objects.filter(
            Q(owner=user) | Q(access_rights__user=user)
        ).distinct()
        return StickyNoteImage.objects.filter(sticky_note__whiteboard__in=accessible_whiteboards)
    
    def get_object(self):
        obj = super().get_object()
        # Check permissions on the whiteboard
        self.check_object_permissions(self.request, obj.sticky_note.whiteboard)
        return obj


class DrawingViewSet(viewsets.ModelViewSet):
    serializer_class = DrawingSerializer
    permission_classes = [permissions.IsAuthenticated, IsWhiteboardOwnerOrHasAccess]
    
    def get_queryset(self):
        user = self.request.user
        # Get drawings from whiteboards user has access to
        accessible_whiteboards = Whiteboard.objects.filter(
            Q(owner=user) | Q(access_rights__user=user)
        ).distinct()
        return Drawing.objects.filter(whiteboard__in=accessible_whiteboards)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CustomColorViewSet(viewsets.ModelViewSet):
    serializer_class = CustomColorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own custom colors
        return CustomColor.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for user management"""
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        # Use different serializer for create/update to handle passwords
        if self.action in ['create', 'update', 'partial_update']:
            from .serializers import UserCreateSerializer
            return UserCreateSerializer
        from .serializers import UserSerializer
        return UserSerializer


class WhiteboardViewSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for user-specific whiteboard view settings"""
    serializer_class = WhiteboardViewSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own view settings
        return WhiteboardViewSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post'])
    def for_whiteboard(self, request):
        """Get or update view settings for a specific whiteboard"""
        whiteboard_id = request.query_params.get('whiteboard_id') or request.data.get('whiteboard')
        
        if not whiteboard_id:
            return Response(
                {'error': 'whiteboard_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user has access to this whiteboard
        try:
            whiteboard = Whiteboard.objects.get(id=whiteboard_id)
            if whiteboard.owner != request.user:
                access = WhiteboardAccess.objects.filter(
                    whiteboard=whiteboard,
                    user=request.user
                ).first()
                if not access:
                    return Response(
                        {'error': 'You do not have access to this whiteboard'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        except Whiteboard.DoesNotExist:
            return Response(
                {'error': 'Whiteboard not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            # Get existing settings or return defaults
            settings = WhiteboardViewSettings.objects.filter(
                user=request.user,
                whiteboard_id=whiteboard_id
            ).first()
            
            if settings:
                serializer = self.get_serializer(settings)
                return Response(serializer.data)
            else:
                # Return default settings
                return Response({
                    'zoom': 1.0,
                    'pan_x': 0.0,
                    'pan_y': 0.0
                })
        
        elif request.method == 'POST':
            # Update or create settings
            settings, created = WhiteboardViewSettings.objects.update_or_create(
                user=request.user,
                whiteboard_id=whiteboard_id,
                defaults={
                    'zoom': request.data.get('zoom', 1.0),
                    'pan_x': request.data.get('pan_x', 0.0),
                    'pan_y': request.data.get('pan_y', 0.0)
                }
            )
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
