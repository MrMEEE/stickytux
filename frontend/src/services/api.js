import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Function to get CSRF token from cookies
function getCsrfToken() {
  const name = 'csrftoken'
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Add CSRF token to all requests
api.interceptors.request.use(
  (config) => {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    // If sending FormData, remove Content-Type to let browser set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default {
  // Whiteboards
  getWhiteboards() {
    return api.get('/whiteboards/')
  },
  
  getWhiteboard(id) {
    return api.get(`/whiteboards/${id}/`)
  },
  
  createWhiteboard(data) {
    return api.post('/whiteboards/', data)
  },
  
  updateWhiteboard(id, data) {
    return api.patch(`/whiteboards/${id}/`, data)
  },
  
  deleteWhiteboard(id) {
    return api.delete(`/whiteboards/${id}/`)
  },
  
  grantAccess(whiteboardId, username, role) {
    return api.post(`/whiteboards/${whiteboardId}/grant_access/`, {
      username,
      role,
    })
  },

  removeAccess(whiteboardId, username) {
    return api.post(`/whiteboards/${whiteboardId}/remove_access/`, {
      username,
    })
  },

  searchUsers(query) {
    return api.get(`/users/search/?q=${encodeURIComponent(query)}`)
  },
  
  // Sticky Notes
  getStickyNotes() {
    return api.get('/sticky-notes/')
  },
  
  createStickyNote(data) {
    return api.post('/sticky-notes/', data)
  },
  
  updateStickyNote(id, data) {
    return api.patch(`/sticky-notes/${id}/`, data)
  },
  
  deleteStickyNote(id) {
    return api.delete(`/sticky-notes/${id}/`)
  },
  
  // Sticky Note Images
  addImageToNote(noteId, imageFile) {
    const formData = new FormData()
    formData.append('image', imageFile)
    return api.post(`/sticky-notes/${noteId}/add_image/`, formData)
  },
  
  deleteNoteImage(imageId) {
    return api.delete(`/sticky-note-images/${imageId}/`)
  },
  
  // Drawings
  getDrawings() {
    return api.get('/drawings/')
  },
  
  createDrawing(data) {
    return api.post('/drawings/', data)
  },
  
  deleteDrawing(id) {
    return api.delete(`/drawings/${id}/`)
  },
  
  // Custom Colors
  getCustomColors() {
    return api.get('/custom-colors/')
  },
  
  createCustomColor(data) {
    return api.post('/custom-colors/', data)
  },
  
  updateCustomColor(id, data) {
    return api.patch(`/custom-colors/${id}/`, data)
  },
  
  deleteCustomColor(id) {
    return api.delete(`/custom-colors/${id}/`)
  },
  
  // View Settings
  getViewSettings(whiteboardId) {
    return api.get('/view-settings/for_whiteboard/', {
      params: { whiteboard_id: whiteboardId }
    })
  },
  
  saveViewSettings(whiteboardId, zoom, panX, panY) {
    return api.post('/view-settings/for_whiteboard/', {
      whiteboard: whiteboardId,
      zoom: zoom,
      pan_x: panX,
      pan_y: panY
    })
  },
  
  // User Administration (admin only)
  getUsers() {
    return api.get('/users/')
  },
  
  createUser(data) {
    return api.post('/users/', data)
  },
  
  updateUser(id, data) {
    return api.patch(`/users/${id}/`, data)
  },
  
  deleteUser(id) {
    return api.delete(`/users/${id}/`)
  },
  
  // Auth
  getCsrfToken() {
    return api.get('/auth/csrf/')
  },
  
  login(username, password) {
    return api.post('/auth/login/', { username, password })
  },
  
  logout() {
    return api.post('/auth/logout/')
  },
}
