<template>
  <div class="whiteboards-view">
    <div class="header">
      <h1>My Whiteboards</h1>
      <button @click="showCreateDialog = true" class="btn btn-primary">Create Whiteboard</button>
    </div>

    <div class="whiteboards-grid">
      <div
        v-for="whiteboard in whiteboards"
        :key="whiteboard.id"
        class="whiteboard-card"
        @click="openWhiteboard(whiteboard.id)"
      >
        <h3>{{ whiteboard.name }}</h3>
        <div class="card-info">
          <p>Created: {{ formatDate(whiteboard.created_at) }}</p>
          <p>Notes: {{ whiteboard.sticky_notes?.length || 0 }}</p>
        </div>
      </div>
    </div>

    <!-- Create Dialog -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="showCreateDialog = false">
      <div class="modal" @click.stop>
        <h2>Create New Whiteboard</h2>
        <input
          v-model="newWhiteboardName"
          type="text"
          placeholder="Whiteboard name"
          class="input"
          @keyup.enter="createWhiteboard"
        />
        <div class="modal-actions">
          <button @click="createWhiteboard" class="btn btn-primary">Create</button>
          <button @click="showCreateDialog = false" class="btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'WhiteboardsView',
  setup() {
    const router = useRouter()
    const whiteboards = ref([])
    const showCreateDialog = ref(false)
    const newWhiteboardName = ref('')

    async function loadWhiteboards() {
      try {
        const response = await api.getWhiteboards()
        whiteboards.value = response.data
      } catch (error) {
        console.error('Error loading whiteboards:', error)
      }
    }

    async function createWhiteboard() {
      if (!newWhiteboardName.value.trim()) return

      try {
        // Ensure we have a CSRF token before making the POST request
        await api.getCsrfToken()
        
        const response = await api.createWhiteboard({
          name: newWhiteboardName.value,
        })
        whiteboards.value.push(response.data)
        showCreateDialog.value = false
        newWhiteboardName.value = ''
        openWhiteboard(response.data.id)
      } catch (error) {
        console.error('Error creating whiteboard:', error)
      }
    }

    function openWhiteboard(id) {
      router.push({ name: 'whiteboard', params: { id } })
    }

    function formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      loadWhiteboards()
    })

    return {
      whiteboards,
      showCreateDialog,
      newWhiteboardName,
      createWhiteboard,
      openWhiteboard,
      formatDate,
    }
  },
}
</script>

<style scoped>
.whiteboards-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.whiteboards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.whiteboard-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.whiteboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.whiteboard-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.card-info p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #4caf50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 30px;
  min-width: 400px;
}

.modal h2 {
  margin-top: 0;
}

.input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
