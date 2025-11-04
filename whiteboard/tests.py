from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Whiteboard, WhiteboardAccess, StickyNote, Drawing


class WhiteboardModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
    def test_create_whiteboard(self):
        """Test creating a whiteboard"""
        whiteboard = Whiteboard.objects.create(
            name='Test Whiteboard',
            owner=self.user
        )
        self.assertEqual(whiteboard.name, 'Test Whiteboard')
        self.assertEqual(whiteboard.owner, self.user)
        
    def test_whiteboard_access(self):
        """Test whiteboard access control"""
        whiteboard = Whiteboard.objects.create(
            name='Test Whiteboard',
            owner=self.user
        )
        other_user = User.objects.create_user(username='other', password='pass')
        
        access = WhiteboardAccess.objects.create(
            whiteboard=whiteboard,
            user=other_user,
            role='edit'
        )
        self.assertEqual(access.role, 'edit')
        self.assertEqual(access.user, other_user)


class StickyNoteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.whiteboard = Whiteboard.objects.create(
            name='Test Whiteboard',
            owner=self.user
        )
        
    def test_create_sticky_note(self):
        """Test creating a sticky note"""
        note = StickyNote.objects.create(
            whiteboard=self.whiteboard,
            content='Test note',
            color='yellow',
            x=100,
            y=100,
            width=200,
            height=200,
            created_by=self.user
        )
        self.assertEqual(note.content, 'Test note')
        self.assertEqual(note.color, 'yellow')
        self.assertEqual(note.created_by, self.user)


class WhiteboardAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
    def test_create_whiteboard_api(self):
        """Test creating a whiteboard via API"""
        data = {'name': 'API Test Whiteboard'}
        response = self.client.post('/api/whiteboards/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Test Whiteboard')
        
    def test_list_whiteboards_api(self):
        """Test listing whiteboards via API"""
        Whiteboard.objects.create(name='Test 1', owner=self.user)
        Whiteboard.objects.create(name='Test 2', owner=self.user)
        
        response = self.client.get('/api/whiteboards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_create_sticky_note_api(self):
        """Test creating a sticky note via API"""
        whiteboard = Whiteboard.objects.create(name='Test', owner=self.user)
        
        data = {
            'whiteboard': whiteboard.id,
            'content': 'Test note',
            'color': 'blue',
            'x': 50,
            'y': 50,
            'width': 200,
            'height': 200
        }
        response = self.client.post('/api/sticky-notes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test note')
        
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access API"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/whiteboards/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

