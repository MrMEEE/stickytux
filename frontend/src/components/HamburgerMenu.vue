<template>
  <div class="hamburger-menu">
    <!-- Hamburger Button -->
    <button 
      @click="isOpen = !isOpen" 
      class="hamburger-btn"
      :class="{ 'open': isOpen }"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>

    <!-- Menu Overlay -->
    <div 
      v-if="isOpen" 
      class="menu-overlay" 
      @click="isOpen = false"
    ></div>

    <!-- Menu Panel -->
    <div class="menu-panel" :class="{ 'open': isOpen }">
      <div class="menu-header">
        <h2>Whiteboards</h2>
        <button @click="isOpen = false" class="close-btn">&times;</button>
      </div>

      <div class="menu-section">
        <button 
          @click="showCreateDialog = true" 
          class="menu-btn primary"
        >
          <span class="icon">+</span>
          Create New Whiteboard
        </button>
      </div>

      <div class="menu-section">
        <h3>My Whiteboards</h3>
        <div class="whiteboard-list">
          <div 
            v-for="whiteboard in whiteboards" 
            :key="whiteboard.id"
            class="whiteboard-item"
          >
            <div class="whiteboard-info" @click="openWhiteboard(whiteboard.id)">
              <span class="whiteboard-name">{{ whiteboard.name }}</span>
              <span class="whiteboard-date">{{ formatDate(whiteboard.created_at) }}</span>
            </div>
            <div class="whiteboard-actions">
              <button 
                @click="showShareDialog(whiteboard)" 
                class="action-btn"
                title="Share whiteboard"
              >
                <span class="icon">👥</span>
              </button>
              <button 
                @click="deleteWhiteboard(whiteboard.id)" 
                class="action-btn danger"
                title="Delete whiteboard"
              >
                <span class="icon">🗑️</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h3>Custom Colors</h3>
        <button 
          @click="showColorDialog = true" 
          class="menu-btn"
        >
          <span class="icon">🎨</span>
          Manage Colors
        </button>
      </div>

      <div class="menu-section">
        <h3>Font Settings</h3>
        <button 
          @click="showFontDialog = true" 
          class="menu-btn"
        >
          <span class="icon">🔤</span>
          Font & Size
        </button>
      </div>

      <div class="menu-section" v-if="currentWhiteboardId">
        <h3>Whiteboard Settings</h3>
        <button 
          @click="showWhiteboardSettingsDialog = true" 
          class="menu-btn"
        >
          <span class="icon">⚙️</span>
          Background Color
        </button>
      </div>

      <div class="menu-section" v-if="isAdmin">
        <h3>User Administration</h3>
        <button 
          @click="showUserAdminDialog = true" 
          class="menu-btn"
        >
          <span class="icon">👤</span>
          Manage Users
        </button>
      </div>
    </div>

    <!-- Create Whiteboard Dialog -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="showCreateDialog = false">
      <div class="modal" @click.stop>
        <h2>Create New Whiteboard</h2>
        <input
          v-model="newWhiteboardName"
          type="text"
          placeholder="Whiteboard name"
          class="input"
          @keyup.enter="createWhiteboard"
          ref="nameInput"
        />
        <div class="modal-actions">
          <button @click="createWhiteboard" class="btn btn-primary">Create</button>
          <button @click="showCreateDialog = false" class="btn">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Share Dialog -->
    <div v-if="shareDialog.visible" class="modal-overlay" @click="closeShareDialog">
      <div class="modal" @click.stop>
        <h2>Share Whiteboard: {{ shareDialog.whiteboard?.name }}</h2>
        
        <div class="share-section">
          <h3>Add User</h3>
          <div class="user-search">
            <input
              v-model="userSearch"
              type="text"
              placeholder="Search for username..."
              class="input"
              @input="searchUsers"
            />
            <select v-model="selectedRole" class="role-select">
              <option value="view">View Only</option>
              <option value="edit">Can Edit</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div v-if="searchResults.length > 0" class="search-results">
            <div 
              v-for="user in searchResults" 
              :key="user.id"
              class="user-result"
              @click="addUserToWhiteboard(user.username)"
            >
              {{ user.username }} ({{ user.email }})
            </div>
          </div>
        </div>

        <div class="share-section">
          <h3>Current Users</h3>
          <div class="current-users">
            <div 
              v-for="access in shareDialog.whiteboard?.user_access || []" 
              :key="access.user"
              class="user-access"
            >
              <span>{{ access.user }}</span>
              <span class="role">{{ access.role }}</span>
              <button 
                @click="removeUserAccess(access.user)" 
                class="remove-btn"
              >
                Remove
              </button>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeShareDialog" class="btn">Close</button>
        </div>
      </div>
    </div>

    <!-- Custom Color Management Dialog -->
    <div v-if="showColorDialog" class="modal-overlay" @click="showColorDialog = false">
      <div class="modal large-modal" @click.stop>
        <h2>Manage Colors</h2>
        
        <div class="share-section">
          <h3>Standard Colors</h3>
          <div class="color-list">
            <div 
              v-for="color in standardColors" 
              :key="color.name"
              class="color-item"
            >
              <div class="color-preview" :style="{ backgroundColor: color.hex }"></div>
              <div class="color-details">
                <input
                  v-model="color.nickname"
                  type="text"
                  :placeholder="color.name"
                  class="input nickname-input"
                  @blur="saveStandardColorNickname(color)"
                />
                <span class="color-hex">{{ color.hex }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="share-section">
          <h3>Add Custom Color</h3>
          <div class="color-form">
            <input
              v-model="newColor.nickname"
              type="text"
              placeholder="Color name (e.g., Housework, Repairs)"
              class="input"
            />
            <div class="color-picker-row">
              <input
                v-model="newColor.hex_color"
                type="color"
                class="color-input"
              />
              <input
                v-model="newColor.hex_color"
                type="text"
                placeholder="#FF5733"
                class="input"
                maxlength="7"
              />
            </div>
            <button @click="createColor" class="btn btn-primary">Add Color</button>
          </div>
        </div>

        <div class="share-section">
          <h3>My Custom Colors</h3>
          <div class="color-list">
            <div 
              v-for="color in customColors" 
              :key="color.id"
              class="color-item"
            >
              <div class="color-preview" :style="{ backgroundColor: color.hex_color }"></div>
              <div class="color-details">
                <span class="color-name">{{ color.nickname || color.name }}</span>
                <span class="color-hex">{{ color.hex_color }}</span>
              </div>
              <button 
                @click="deleteColor(color.id)" 
                class="remove-btn"
              >
                Delete
              </button>
            </div>
            <div v-if="customColors.length === 0" class="empty-state">
              No custom colors yet. Add one above!
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="showColorDialog = false" class="btn">Close</button>
        </div>
      </div>
    </div>

    <!-- User Administration Dialog -->
    <div v-if="showUserAdminDialog" class="modal-overlay" @click="showUserAdminDialog = false">
      <div class="modal large-modal" @click.stop>
        <h2>User Administration</h2>
        
        <div class="user-admin-section">
          <h3>Create New User</h3>
          <div class="user-form">
            <input
              v-model="newUser.username"
              type="text"
              placeholder="Username"
              class="input"
            />
            <input
              v-model="newUser.email"
              type="email"
              placeholder="Email"
              class="input"
            />
            <input
              v-model="newUser.password"
              type="password"
              placeholder="Password"
              class="input"
            />
            <label class="checkbox-label">
              <input v-model="newUser.is_staff" type="checkbox" />
              <span>Admin User</span>
            </label>
            <button @click="createNewUser" class="btn btn-primary">
              Create User
            </button>
          </div>
        </div>

        <div class="user-admin-section">
          <h3>Existing Users</h3>
          <div class="user-list">
            <div 
              v-for="user in users" 
              :key="user.id"
              class="user-item"
            >
              <div class="user-info">
                <span class="username">{{ user.username }}</span>
                <span class="email">{{ user.email }}</span>
                <span class="badge" v-if="user.is_staff">Admin</span>
                <span class="badge inactive" v-if="!user.is_active">Inactive</span>
              </div>
              <div class="user-actions">
                <button 
                  @click="toggleUserAdmin(user)" 
                  class="action-btn"
                  :title="user.is_staff ? 'Remove admin' : 'Make admin'"
                >
                  {{ user.is_staff ? '⭐' : '☆' }}
                </button>
                <button 
                  @click="toggleUserActive(user)" 
                  class="action-btn"
                  :title="user.is_active ? 'Deactivate' : 'Activate'"
                >
                  {{ user.is_active ? '✓' : '✗' }}
                </button>
                <button 
                  @click="showResetPasswordDialog(user)" 
                  class="action-btn"
                  title="Reset password"
                >
                  🔑
                </button>
                <button 
                  @click="confirmDeleteUser(user)" 
                  class="action-btn danger"
                  title="Delete user"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="showUserAdminDialog = false" class="btn">Close</button>
        </div>
      </div>
    </div>

    <!-- Reset Password Dialog -->
    <div v-if="resetPasswordDialog.visible" class="modal-overlay" @click="closeResetPasswordDialog">
      <div class="modal" @click.stop>
        <h2>Reset Password for {{ resetPasswordDialog.user?.username }}</h2>
        <input
          v-model="resetPasswordDialog.newPassword"
          type="password"
          placeholder="New password"
          class="input"
          @keyup.enter="resetUserPassword"
        />
        <div class="modal-actions">
          <button @click="resetUserPassword" class="btn btn-primary">Reset Password</button>
          <button @click="closeResetPasswordDialog" class="btn">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Font Settings Dialog -->
    <div v-if="showFontDialog" class="modal-overlay" @click="showFontDialog = false">
      <div class="modal" @click.stop>
        <h2>Font & Size Settings</h2>
        
        <div class="font-section">
          <h3>Default Font Family</h3>
          <select v-model="fontSettings.family" class="input">
            <option value="'Comic Sans MS', cursive">Comic Sans MS (Default)</option>
            <option value="Arial, sans-serif">Arial</option>
            <option value="'Times New Roman', serif">Times New Roman</option>
            <option value="Georgia, serif">Georgia</option>
            <option value="'Courier New', monospace">Courier New</option>
            <option value="Verdana, sans-serif">Verdana</option>
            <option value="Tahoma, sans-serif">Tahoma</option>
            <option value="'Trebuchet MS', sans-serif">Trebuchet MS</option>
            <option value="Impact, sans-serif">Impact</option>
            <option value="'Brush Script MT', cursive">Brush Script</option>
          </select>
          <div class="preview-text" :style="{ fontFamily: fontSettings.family, color: fontSettings.color }">
            Preview: The quick brown fox jumps over the lazy dog
          </div>
        </div>

        <div class="font-section">
          <h3>Default Font Color</h3>
          <div class="color-picker-row">
            <input 
              type="color" 
              v-model="fontSettings.color" 
              class="color-input"
            />
            <span class="color-value">{{ fontSettings.color }}</span>
          </div>
        </div>

        <div class="font-section">
          <h3>Sticky Note Font Size</h3>
          <div class="size-control">
            <input 
              type="range" 
              v-model.number="fontSettings.noteFontSize" 
              min="12" 
              max="24" 
              step="1"
              class="slider"
            />
            <span class="size-value">{{ fontSettings.noteFontSize }}px</span>
          </div>
          <div class="preview-note" :style="{ fontFamily: fontSettings.family, fontSize: fontSettings.noteFontSize + 'px', color: fontSettings.color }">
            Sticky Note Preview
          </div>
        </div>

        <div class="font-section">
          <h3>Text Element Font Size</h3>
          <div class="size-control">
            <input 
              type="range" 
              v-model.number="fontSettings.textFontSize" 
              min="14" 
              max="48" 
              step="2"
              class="slider"
            />
            <span class="size-value">{{ fontSettings.textFontSize }}px</span>
          </div>
          <div class="preview-text" :style="{ fontFamily: fontSettings.family, fontSize: fontSettings.textFontSize + 'px', color: fontSettings.color }">
            Text Element Preview
          </div>
        </div>

        <div class="modal-actions">
          <button @click="saveFontSettings" class="btn btn-primary">Save Settings</button>
          <button @click="showFontDialog = false" class="btn">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Whiteboard Settings Dialog -->
    <div v-if="showWhiteboardSettingsDialog" class="modal-overlay" @click="showWhiteboardSettingsDialog = false">
      <div class="modal" @click.stop>
        <h2>Whiteboard Settings</h2>
        
        <div class="font-section">
          <h3>Background Color</h3>
          <div class="color-picker-row">
            <input 
              type="color" 
              v-model="whiteboardBackgroundColor" 
              class="color-input"
            />
            <span class="color-value">{{ whiteboardBackgroundColor }}</span>
          </div>
          <div class="preview-text" :style="{ backgroundColor: whiteboardBackgroundColor, padding: '20px', marginTop: '10px' }">
            Whiteboard Preview
          </div>
        </div>

        <div class="modal-actions">
          <button @click="saveWhiteboardSettings" class="btn btn-primary">Save Settings</button>
          <button @click="showWhiteboardSettingsDialog = false" class="btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'HamburgerMenu',
  props: {
    currentWhiteboardId: {
      type: Number,
      default: null
    },
    initialBackgroundColor: {
      type: String,
      default: '#ffffff'
    }
  },
  emits: ['update-background-color'],
  setup(props, { emit }) {
    const router = useRouter()
    
    // Menu state
    const isOpen = ref(false)
    const whiteboards = ref([])
    
    // Create dialog
    const showCreateDialog = ref(false)
    const newWhiteboardName = ref('')
    const nameInput = ref(null)
    
    // Share dialog
    const shareDialog = ref({
      visible: false,
      whiteboard: null
    })
    const userSearch = ref('')
    const searchResults = ref([])
    const selectedRole = ref('edit')

    // Custom colors
    const showColorDialog = ref(false)
    const customColors = ref([])
    const standardColors = ref([
      { name: 'yellow', hex: '#fef08a', nickname: '' },
      { name: 'pink', hex: '#fbcfe8', nickname: '' },
      { name: 'blue', hex: '#bfdbfe', nickname: '' },
      { name: 'green', hex: '#bbf7d0', nickname: '' },
      { name: 'orange', hex: '#fed7aa', nickname: '' },
      { name: 'purple', hex: '#e9d5ff', nickname: '' }
    ])
    const newColor = ref({
      name: '',
      nickname: '',
      hex_color: '#FF5733'
    })

    // User administration
    const isAdmin = ref(false)
    const showUserAdminDialog = ref(false)
    const users = ref([])
    const newUser = ref({
      username: '',
      email: '',
      password: '',
      is_staff: false,
      is_active: true
    })
    const resetPasswordDialog = ref({
      visible: false,
      user: null,
      newPassword: ''
    })

    // Font settings
    const showFontDialog = ref(false)
    const fontSettings = ref({
      family: "'Comic Sans MS', cursive",
      noteFontSize: 14,
      textFontSize: 16,
      color: '#333333'
    })

    // Whiteboard settings
    const showWhiteboardSettingsDialog = ref(false)
    const whiteboardBackgroundColor = ref(props.initialBackgroundColor)

    // Methods
    const loadWhiteboards = async () => {
      try {
        const response = await api.getWhiteboards()
        whiteboards.value = response.data
      } catch (error) {
        console.error('Error loading whiteboards:', error)
      }
    }

    const createWhiteboard = async () => {
      if (!newWhiteboardName.value.trim()) return
      
      try {
        // Ensure we have a CSRF token before making the POST request
        await api.getCsrfToken()
        
        const response = await api.createWhiteboard({
          name: newWhiteboardName.value.trim()
        })
        whiteboards.value.push(response.data)
        newWhiteboardName.value = ''
        showCreateDialog.value = false
        // Navigate to new whiteboard
        router.push(`/whiteboard/${response.data.id}`)
      } catch (error) {
        console.error('Error creating whiteboard:', error)
        alert('Failed to create whiteboard')
      }
    }

    const openWhiteboard = (id) => {
      isOpen.value = false
      router.push(`/whiteboard/${id}`)
    }

    const deleteWhiteboard = async (id) => {
      if (!confirm('Are you sure you want to delete this whiteboard?')) return
      
      try {
        await api.deleteWhiteboard(id)
        whiteboards.value = whiteboards.value.filter(wb => wb.id !== id)
      } catch (error) {
        console.error('Error deleting whiteboard:', error)
        alert('Failed to delete whiteboard')
      }
    }

    const showShareDialog = (whiteboard) => {
      shareDialog.value = {
        visible: true,
        whiteboard: whiteboard
      }
    }

    const closeShareDialog = () => {
      shareDialog.value = {
        visible: false,
        whiteboard: null
      }
      userSearch.value = ''
      searchResults.value = []
    }

    const searchUsers = async () => {
      if (userSearch.value.length < 2) {
        searchResults.value = []
        return
      }
      
      try {
        // Note: This endpoint would need to be implemented in the backend
        const response = await api.searchUsers(userSearch.value)
        searchResults.value = response.data
      } catch (error) {
        console.error('Error searching users:', error)
        searchResults.value = []
      }
    }

    const addUserToWhiteboard = async (username) => {
      try {
        await api.grantAccess(
          shareDialog.value.whiteboard.id, 
          username, 
          selectedRole.value
        )
        // Refresh whiteboard data
        loadWhiteboards()
        userSearch.value = ''
        searchResults.value = []
      } catch (error) {
        console.error('Error adding user:', error)
        alert('Failed to add user to whiteboard')
      }
    }

    const removeUserAccess = async (username) => {
      try {
        // Note: This endpoint would need to be implemented in the backend
        await api.removeAccess(shareDialog.value.whiteboard.id, username)
        loadWhiteboards()
      } catch (error) {
        console.error('Error removing user:', error)
        alert('Failed to remove user access')
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    // Custom color management
    const loadCustomColors = async () => {
      try {
        const response = await api.getCustomColors()
        customColors.value = response.data
      } catch (error) {
        console.error('Error loading custom colors:', error)
      }
    }

    const createColor = async () => {
      if (!newColor.value.nickname.trim() || !newColor.value.hex_color) return
      
      try {
        // Generate unique name from nickname (lowercase, replace spaces with underscores)
        const name = 'custom_' + Date.now()
        const response = await api.createCustomColor({
          name: name,
          nickname: newColor.value.nickname.trim(),
          hex_color: newColor.value.hex_color
        })
        customColors.value.push(response.data)
        newColor.value = {
          name: '',
          nickname: '',
          hex_color: '#FF5733'
        }
      } catch (error) {
        console.error('Error creating color:', error)
        alert('Failed to create color')
      }
    }

    const deleteColor = async (id) => {
      if (!confirm('Are you sure you want to delete this color?')) return
      
      try {
        await api.deleteCustomColor(id)
        customColors.value = customColors.value.filter(c => c.id !== id)
      } catch (error) {
        console.error('Error deleting color:', error)
        alert('Failed to delete color')
      }
    }

    const loadStandardColorNicknames = () => {
      const saved = localStorage.getItem('standardColorNicknames')
      if (saved) {
        try {
          const nicknames = JSON.parse(saved)
          standardColors.value.forEach(color => {
            if (nicknames[color.name]) {
              color.nickname = nicknames[color.name]
            }
          })
        } catch (error) {
          console.error('Error loading standard color nicknames:', error)
        }
      }
    }

    const saveStandardColorNickname = (color) => {
      const saved = localStorage.getItem('standardColorNicknames')
      let nicknames = {}
      if (saved) {
        try {
          nicknames = JSON.parse(saved)
        } catch (error) {
          console.error('Error parsing saved nicknames:', error)
        }
      }
      nicknames[color.name] = color.nickname
      localStorage.setItem('standardColorNicknames', JSON.stringify(nicknames))
    }

    // User administration
    const loadUsers = async () => {
      try {
        const response = await api.getUsers()
        users.value = response.data
      } catch (error) {
        console.error('Error loading users:', error)
        if (error.response?.status === 403) {
          isAdmin.value = false
        }
      }
    }

    const createNewUser = async () => {
      if (!newUser.value.username || !newUser.value.password) {
        alert('Username and password are required')
        return
      }

      try {
        await api.createUser(newUser.value)
        newUser.value = {
          username: '',
          email: '',
          password: '',
          is_staff: false,
          is_active: true
        }
        await loadUsers()
      } catch (error) {
        console.error('Error creating user:', error)
        alert('Failed to create user: ' + (error.response?.data?.username?.[0] || error.message))
      }
    }

    const toggleUserAdmin = async (user) => {
      try {
        await api.updateUser(user.id, { is_staff: !user.is_staff })
        await loadUsers()
      } catch (error) {
        console.error('Error updating user:', error)
        alert('Failed to update user')
      }
    }

    const toggleUserActive = async (user) => {
      try {
        await api.updateUser(user.id, { is_active: !user.is_active })
        await loadUsers()
      } catch (error) {
        console.error('Error updating user:', error)
        alert('Failed to update user')
      }
    }

    const showResetPasswordDialog = (user) => {
      resetPasswordDialog.value = {
        visible: true,
        user: user,
        newPassword: ''
      }
    }

    const closeResetPasswordDialog = () => {
      resetPasswordDialog.value = {
        visible: false,
        user: null,
        newPassword: ''
      }
    }

    const resetUserPassword = async () => {
      if (!resetPasswordDialog.value.newPassword) {
        alert('Password cannot be empty')
        return
      }

      try {
        await api.updateUser(resetPasswordDialog.value.user.id, {
          password: resetPasswordDialog.value.newPassword
        })
        closeResetPasswordDialog()
        alert('Password reset successfully')
      } catch (error) {
        console.error('Error resetting password:', error)
        alert('Failed to reset password')
      }
    }

    const confirmDeleteUser = async (user) => {
      if (!confirm(`Are you sure you want to delete user "${user.username}"? This action cannot be undone.`)) {
        return
      }

      try {
        await api.deleteUser(user.id)
        await loadUsers()
      } catch (error) {
        console.error('Error deleting user:', error)
        alert('Failed to delete user')
      }
    }

    const checkAdminStatus = async () => {
      try {
        // Try to load users - if successful, user is admin
        const response = await api.getUsers()
        isAdmin.value = true
        users.value = response.data
      } catch (error) {
        isAdmin.value = false
      }
    }

    // Font settings
    const loadFontSettings = () => {
      const saved = localStorage.getItem('fontSettings')
      if (saved) {
        try {
          const settings = JSON.parse(saved)
          fontSettings.value = {
            family: settings.family || "'Comic Sans MS', cursive",
            noteFontSize: settings.noteFontSize || 14,
            textFontSize: settings.textFontSize || 16,
            color: settings.color || '#333333'
          }
          applyFontSettings()
        } catch (error) {
          console.error('Error loading font settings:', error)
        }
      }
    }

    const saveFontSettings = () => {
      localStorage.setItem('fontSettings', JSON.stringify(fontSettings.value))
      applyFontSettings()
      showFontDialog.value = false
    }

    const applyFontSettings = () => {
      // Apply font settings to CSS variables
      document.documentElement.style.setProperty('--note-font-family', fontSettings.value.family)
      document.documentElement.style.setProperty('--note-font-size', fontSettings.value.noteFontSize + 'px')
      document.documentElement.style.setProperty('--text-font-size', fontSettings.value.textFontSize + 'px')
      document.documentElement.style.setProperty('--note-font-color', fontSettings.value.color)
    }

    // Whiteboard settings
    const saveWhiteboardSettings = async () => {
      if (!props.currentWhiteboardId) return
      
      try {
        await api.updateWhiteboard(props.currentWhiteboardId, {
          background_color: whiteboardBackgroundColor.value
        })
        emit('update-background-color', whiteboardBackgroundColor.value)
        showWhiteboardSettingsDialog.value = false
      } catch (error) {
        console.error('Error saving whiteboard settings:', error)
        alert('Failed to save whiteboard settings')
      }
    }

    // Watch for create dialog opening to focus input
    const handleCreateDialog = async () => {
      if (showCreateDialog.value) {
        await nextTick()
        nameInput.value?.focus()
      }
    }

    // Watch for user admin dialog opening to load users
    const handleUserAdminDialog = async () => {
      if (showUserAdminDialog.value) {
        await loadUsers()
      }
    }

    // Load whiteboards, custom colors, check admin status, and load font settings on mount
    onMounted(() => {
      loadWhiteboards()
      loadCustomColors()
      loadStandardColorNicknames()
      checkAdminStatus()
      loadFontSettings()
    })

    // Watch for prop changes
    watch(() => props.initialBackgroundColor, (newColor) => {
      whiteboardBackgroundColor.value = newColor
    })

    return {
      isOpen,
      whiteboards,
      showCreateDialog,
      newWhiteboardName,
      nameInput,
      shareDialog,
      userSearch,
      searchResults,
      selectedRole,
      showColorDialog,
      customColors,
      standardColors,
      newColor,
      isAdmin,
      showUserAdminDialog,
      users,
      newUser,
      resetPasswordDialog,
      loadWhiteboards,
      createWhiteboard,
      openWhiteboard,
      deleteWhiteboard,
      showShareDialog,
      closeShareDialog,
      searchUsers,
      addUserToWhiteboard,
      removeUserAccess,
      formatDate,
      handleCreateDialog,
      loadCustomColors,
      createColor,
      deleteColor,
      saveStandardColorNickname,
      loadUsers,
      createNewUser,
      toggleUserAdmin,
      toggleUserActive,
      showResetPasswordDialog,
      closeResetPasswordDialog,
      resetUserPassword,
      confirmDeleteUser,
      handleUserAdminDialog,
      showFontDialog,
      fontSettings,
      saveFontSettings,
      showWhiteboardSettingsDialog,
      whiteboardBackgroundColor,
      saveWhiteboardSettings
    }
  },
  watch: {
    showCreateDialog(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.$refs.nameInput?.focus()
        })
      }
    },
    showUserAdminDialog(newVal) {
      if (newVal) {
        this.handleUserAdminDialog()
      }
    }
  }
}
</script>

<style scoped>
.hamburger-menu {
  position: relative;
  z-index: 1000;
  margin-right: 10px;
}

.hamburger-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.hamburger-btn span {
  width: 20px;
  height: 2px;
  background: white;
  transition: all 0.3s ease;
}

.hamburger-btn.open span:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.hamburger-btn.open span:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.open span:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.menu-panel {
  position: fixed;
  top: 0;
  left: -350px;
  width: 350px;
  height: 100vh;
  background: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: left 0.3s ease;
  z-index: 1001;
  overflow-y: auto;
}

.menu-panel.open {
  left: 0;
}

.menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.menu-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.menu-section {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.menu-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.menu-btn {
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  background: #f5f5f5;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.menu-btn:hover {
  background: #ebebeb;
}

.menu-btn.primary {
  background: #007bff;
  color: white;
}

.menu-btn.primary:hover {
  background: #0056b3;
}

.whiteboard-list {
  max-height: 300px;
  overflow-y: auto;
}

.whiteboard-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.whiteboard-item:last-child {
  border-bottom: none;
}

.whiteboard-info {
  flex: 1;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.whiteboard-info:hover {
  background: #f8f9fa;
}

.whiteboard-name {
  display: block;
  font-weight: 500;
  color: #333;
}

.whiteboard-date {
  display: block;
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.whiteboard-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #ebebeb;
}

.action-btn.danger:hover {
  background: #dc3545;
  color: white;
}

.icon {
  font-size: 14px;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h2 {
  margin: 0 0 20px 0;
  color: #333;
}

.input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #333;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn:hover {
  background: #f8f9fa;
}

.btn-primary {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.btn-primary:hover {
  background: #0056b3;
  border-color: #0056b3;
}

/* Share dialog specific styles */
.share-section {
  margin-bottom: 24px;
}

.share-section h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.user-search {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.role-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.search-results {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.user-result {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

.user-result:hover {
  background: #f8f9fa;
}

.user-result:last-child {
  border-bottom: none;
}

.current-users {
  max-height: 200px;
  overflow-y: auto;
}

.user-access {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.user-access:last-child {
  border-bottom: none;
}

.role {
  padding: 2px 8px;
  background: #e9ecef;
  border-radius: 12px;
  font-size: 12px;
  color: #495057;
}

.remove-btn {
  padding: 4px 8px;
  border: 1px solid #dc3545;
  border-radius: 4px;
  background: white;
  color: #dc3545;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #dc3545;
  color: white;
}

/* Custom Color Management */
.color-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-picker-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.color-input {
  width: 60px;
  height: 40px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.color-list {
  max-height: 300px;
  overflow-y: auto;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.color-item:last-child {
  border-bottom: none;
}

.color-preview {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  border: 1px solid #ddd;
  flex-shrink: 0;
}

.color-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nickname-input {
  font-size: 14px;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-weight: 500;
}

.nickname-input:focus {
  outline: none;
  border-color: #007bff;
}

.color-name {
  font-weight: 500;
  color: #333;
}

.color-hex {
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #999;
  font-style: italic;
}

/* User Administration */
.large-modal {
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
}

.user-admin-section {
  margin-bottom: 30px;
}

.user-admin-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.username {
  font-weight: 600;
  color: #333;
}

.email {
  font-size: 13px;
  color: #666;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  background: #007bff;
  color: white;
  font-size: 11px;
  border-radius: 12px;
  margin-top: 4px;
  align-self: flex-start;
}

.badge.inactive {
  background: #6c757d;
}

.user-actions {
  display: flex;
  gap: 8px;
}

/* Font Settings */
.font-section {
  margin-bottom: 25px;
}

.font-section h3 {
  margin-bottom: 12px;
  font-size: 15px;
  color: #333;
  font-weight: 600;
}

.size-control {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #ddd;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
  border: none;
}

.size-value {
  min-width: 50px;
  font-weight: 600;
  color: #007bff;
}

.color-picker-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-input {
  width: 60px;
  height: 40px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.color-value {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.preview-text {
  padding: 15px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  color: #333;
}

.preview-note {
  padding: 12px;
  background: #fef9c3;
  border: 1px solid #f59e0b;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  color: #333;
}
</style>