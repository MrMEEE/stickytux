from django.db import models
from django.contrib.auth.models import User


class Whiteboard(models.Model):
    """Represents a whiteboard that can contain multiple sticky notes"""
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_whiteboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    background_color = models.CharField(max_length=7, default='#ffffff')  # Hex color
    
    def __str__(self):
        return self.name


class WhiteboardAccess(models.Model):
    """Manages user access to whiteboards"""
    ROLE_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'Can Edit'),
        ('admin', 'Admin'),
    ]
    
    whiteboard = models.ForeignKey(Whiteboard, on_delete=models.CASCADE, related_name='access_rights')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whiteboard_access')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='view')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['whiteboard', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.whiteboard.name} ({self.role})"


class StickyNote(models.Model):
    """Represents a sticky note on a whiteboard"""
    COLOR_CHOICES = [
        ('yellow', 'Yellow'),
        ('pink', 'Pink'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('purple', 'Purple'),
    ]
    
    whiteboard = models.ForeignKey(Whiteboard, on_delete=models.CASCADE, related_name='sticky_notes')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='sticky_notes/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='yellow')
    
    # Position and size
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    width = models.FloatField(default=200)
    height = models.FloatField(default=200)
    
    # Grouping
    group_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    z_index = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Note on {self.whiteboard.name} at ({self.x}, {self.y})"


class StickyNoteImage(models.Model):
    """Represents an image attached to a sticky note"""
    sticky_note = models.ForeignKey(StickyNote, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='sticky_notes/')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.sticky_note}"


class Drawing(models.Model):
    """Represents freehand drawing on a whiteboard"""
    whiteboard = models.ForeignKey(Whiteboard, on_delete=models.CASCADE, related_name='drawings')
    path_data = models.TextField()  # SVG path data
    color = models.CharField(max_length=20, default='black')
    stroke_width = models.FloatField(default=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drawings')
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Drawing on {self.whiteboard.name}"


class CustomColor(models.Model):
    """Represents a custom color defined by a user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_colors')
    name = models.CharField(max_length=50)  # Internal identifier (e.g., 'custom1', 'custom2')
    nickname = models.CharField(max_length=100, blank=True)  # User-friendly name (e.g., 'Housework', 'Repairs')
    hex_color = models.CharField(max_length=7)  # Hex color value (e.g., '#FF5733')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.nickname or self.name} ({self.hex_color}) - {self.user.username}"


class WhiteboardViewSettings(models.Model):
    """Stores user-specific view settings for a whiteboard"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whiteboard_view_settings')
    whiteboard = models.ForeignKey(Whiteboard, on_delete=models.CASCADE, related_name='view_settings')
    zoom = models.FloatField(default=1.0)
    pan_x = models.FloatField(default=0.0)
    pan_y = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'whiteboard']
    
    def __str__(self):
        return f"{self.user.username} - {self.whiteboard.name} (zoom: {self.zoom})"

