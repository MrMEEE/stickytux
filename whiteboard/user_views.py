from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search for users by username or email"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return Response([])
    
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]  # Exclude current user, limit to 10 results
    
    user_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        for user in users
    ]
    
    return Response(user_data)