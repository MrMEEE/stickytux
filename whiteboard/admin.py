from django.contrib import admin
from .models import Whiteboard, WhiteboardAccess, StickyNote, StickyNoteImage, Drawing, CustomColor


@admin.register(Whiteboard)
class WhiteboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'owner__username']


@admin.register(WhiteboardAccess)
class WhiteboardAccessAdmin(admin.ModelAdmin):
    list_display = ['whiteboard', 'user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['whiteboard__name', 'user__username']


@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    list_display = ['whiteboard', 'color', 'x', 'y', 'created_by', 'created_at']
    list_filter = ['color', 'created_at']
    search_fields = ['content', 'whiteboard__name']


@admin.register(StickyNoteImage)
class StickyNoteImageAdmin(admin.ModelAdmin):
    list_display = ['sticky_note', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sticky_note__content']


@admin.register(Drawing)
class DrawingAdmin(admin.ModelAdmin):
    list_display = ['whiteboard', 'color', 'created_by', 'created_at']
    list_filter = ['color', 'created_at']
    search_fields = ['whiteboard__name']


@admin.register(CustomColor)
class CustomColorAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'nickname', 'hex_color', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'nickname', 'user__username']


