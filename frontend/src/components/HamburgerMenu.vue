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
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'HamburgerMenu',
  setup() {
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

    // Watch for create dialog opening to focus input
    const handleCreateDialog = async () => {
      if (showCreateDialog.value) {
        await nextTick()
        nameInput.value?.focus()
      }
    }

    // Load whiteboards on mount
    onMounted(() => {
      loadWhiteboards()
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
      handleCreateDialog
    }
  },
  watch: {
    showCreateDialog(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.$refs.nameInput?.focus()
        })
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
</style>