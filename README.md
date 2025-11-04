# StickyTux

A collaborative whiteboard application with sticky notes, built with Django, Vue.js, and WebSockets.

## Features

### Core Features
- **Multi-user collaboration** - Real-time updates via WebSockets
- **Multiple Whiteboards** - Create and manage multiple whiteboards
- **Access Control** - Variable access levels (view, edit, admin) for users
- **Sticky Notes** - Drag, resize, and customize sticky notes
- **Freehand Drawing** - Draw directly on the whiteboard
- **Rich Content** - Support for text, images, and links in sticky notes
- **Color Customization** - Multiple color options for sticky notes

### Navigation
- **Zoom In/Out** - Use mouse wheel to zoom
- **Pan** - Middle mouse button to drag around the whiteboard
- **Right-Click Menu** - Context menu to add sticky notes

### Sticky Note Features
- Draggable positioning
- Resizable dimensions
- Multi-select and group operations (Ctrl/Cmd + click)
- Multiple colors (yellow, pink, blue, green, orange, purple)
- Text content
- Image attachments
- Embedded links
- Delete functionality

## Tech Stack

### Backend
- **Django 5.x** - Web framework
- **Django REST Framework** - API framework
- **Channels** - WebSocket support
- **SQLite** - Database (default, can be changed)
- **Pillow** - Image processing

### Frontend
- **Vue 3** - JavaScript framework
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client
- **WebSocket** - Real-time communication

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser:
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. Open the frontend in your browser (`http://localhost:5173`)
2. Log in with your superuser credentials
3. Create a new whiteboard
4. Start adding sticky notes and drawings!

### Controls

- **Mouse Wheel** - Zoom in/out
- **Middle Mouse Button + Drag** - Pan around the whiteboard
- **Right Click** - Open context menu to add sticky notes
- **Left Click + Drag** - Move sticky notes
- **Ctrl/Cmd + Click** - Multi-select sticky notes
- **Draw Mode** - Enable to draw freehand on the whiteboard
- **Resize Handle** - Bottom-right corner of each sticky note

### Multi-User Collaboration

The application uses WebSockets for real-time collaboration. When multiple users are viewing the same whiteboard:
- Changes are broadcast to all connected users
- Sticky notes appear instantly for all users
- Drawings are shared in real-time

### Access Control

Whiteboard owners can grant access to other users:
- **View** - Read-only access
- **Edit** - Can add, modify, and delete sticky notes
- **Admin** - Can manage access rights

## API Endpoints

### Whiteboards
- `GET /api/whiteboards/` - List all accessible whiteboards
- `POST /api/whiteboards/` - Create a new whiteboard
- `GET /api/whiteboards/{id}/` - Get whiteboard details
- `PATCH /api/whiteboards/{id}/` - Update whiteboard
- `DELETE /api/whiteboards/{id}/` - Delete whiteboard
- `POST /api/whiteboards/{id}/grant_access/` - Grant user access

### Sticky Notes
- `GET /api/sticky-notes/` - List all accessible sticky notes
- `POST /api/sticky-notes/` - Create a new sticky note
- `PATCH /api/sticky-notes/{id}/` - Update sticky note
- `DELETE /api/sticky-notes/{id}/` - Delete sticky note

### Drawings
- `GET /api/drawings/` - List all accessible drawings
- `POST /api/drawings/` - Create a new drawing
- `DELETE /api/drawings/{id}/` - Delete drawing

### WebSocket
- `ws://localhost:8000/ws/whiteboard/{id}/` - Connect to whiteboard for real-time updates

## Development

### Project Structure
```
stickytux/
├── backend/              # Django settings
├── whiteboard/           # Main Django app
│   ├── models.py        # Database models
│   ├── views.py         # API views
│   ├── serializers.py   # DRF serializers
│   ├── consumers.py     # WebSocket consumers
│   └── routing.py       # WebSocket routing
├── frontend/            # Vue.js application
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── views/       # Page views
│   │   ├── services/    # API service
│   │   └── router/      # Vue Router config
│   └── package.json
├── manage.py
└── requirements.txt
```

### Running Tests

Backend tests:
```bash
python manage.py test
```

Frontend tests:
```bash
cd frontend
npm run test
```

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in Django settings
2. Configure a proper database (PostgreSQL recommended)
3. Set up Redis for Channels layer
4. Configure static file serving
5. Use a production ASGI server (Daphne, Uvicorn)
6. Build the frontend: `npm run build`
7. Serve the frontend build with a web server (Nginx, Apache)

## License

See LICENSE file for details.

