import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
