from django.db import models
from django.contrib.auth.models import User


class Whiteboard(models.Model):
    """Represents a whiteboard that can contain multiple sticky notes"""
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_whiteboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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


class Drawing(models.Model):
    """Represents freehand drawing on a whiteboard"""
    whiteboard = models.ForeignKey(Whiteboard, on_delete=models.CASCADE, related_name='drawings')
    path_data = models.TextField()  # SVG path data
    color = models.CharField(max_length=20, default='black')
    stroke_width = models.FloatField(default=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drawings')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Drawing on {self.whiteboard.name}"

