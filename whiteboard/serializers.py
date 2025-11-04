from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Whiteboard, WhiteboardAccess, StickyNote, Drawing


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class WhiteboardAccessSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WhiteboardAccess
        fields = ['id', 'user', 'role', 'created_at']


class StickyNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = StickyNote
        fields = [
            'id', 'whiteboard', 'content', 'image', 'link', 'color',
            'x', 'y', 'width', 'height', 'group_id', 'z_index',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class DrawingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Drawing
        fields = ['id', 'whiteboard', 'path_data', 'color', 'stroke_width', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class WhiteboardSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    sticky_notes = StickyNoteSerializer(many=True, read_only=True)
    drawings = DrawingSerializer(many=True, read_only=True)
    access_rights = WhiteboardAccessSerializer(many=True, read_only=True)
    
    class Meta:
        model = Whiteboard
        fields = ['id', 'name', 'owner', 'sticky_notes', 'drawings', 'access_rights', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
