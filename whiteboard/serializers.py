from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Whiteboard, WhiteboardAccess, StickyNote, StickyNoteImage, Drawing, CustomColor, WhiteboardViewSettings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating users with password handling"""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class WhiteboardAccessSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WhiteboardAccess
        fields = ['id', 'user', 'role', 'created_at']


class StickyNoteImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StickyNoteImage
        fields = ['id', 'image', 'order', 'created_at']
        read_only_fields = ['created_at']


class StickyNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    images = StickyNoteImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = StickyNote
        fields = [
            'id', 'whiteboard', 'content', 'image', 'images', 'link', 'color',
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
        fields = ['id', 'name', 'owner', 'sticky_notes', 'drawings', 'access_rights', 'background_color', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class CustomColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomColor
        fields = ['id', 'name', 'nickname', 'hex_color', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WhiteboardViewSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhiteboardViewSettings
        fields = ['id', 'whiteboard', 'zoom', 'pan_x', 'pan_y', 'updated_at']
        read_only_fields = ['updated_at']
