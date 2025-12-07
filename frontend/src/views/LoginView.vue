<template>
  <div class="login-view">
    <div class="login-card">
      <h1>StickyTux</h1>
      <p class="subtitle">Collaborative Whiteboard</p>

      <form @submit.prevent="handleLogin">
        <input
          v-model="username"
          type="text"
          placeholder="Username"
          class="input"
          required
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="input"
          required
        />
        <button type="submit" class="btn btn-primary">Login</button>
      </form>

      <p class="info-text">
        For demo purposes, create a superuser with: <br />
        <code>python manage.py createsuperuser</code>
      </p>

      <!-- Debug Information -->
      <div class="debug-info">
        <h4>Debug Info:</h4>
        <p><strong>API Base URL:</strong> {{ debugInfo.apiUrl }}</p>
        <p><strong>Current Host:</strong> {{ debugInfo.hostname }}</p>
        <p><strong>Protocol:</strong> {{ debugInfo.protocol }}</p>
        <button @click="testConnection" type="button" class="btn btn-secondary">Test API Connection</button>
        <div v-if="connectionTest" class="connection-test" :class="connectionTest.success ? 'success' : 'error'">
          {{ connectionTest.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const connectionTest = ref(null)
    
    // Debug information
    const debugInfo = ref({
      apiUrl: '',
      hostname: window.location.hostname,
      protocol: window.location.protocol
    })

    // Get API URL (same logic as in api.js)
    if (process.env.NODE_ENV === 'production' || window.location.hostname !== 'localhost') {
      const protocol = window.location.protocol
      const hostname = window.location.hostname.replace('frontend', 'backend')
      debugInfo.value.apiUrl = `${protocol}//${hostname}/api`
    } else {
      debugInfo.value.apiUrl = 'http://localhost:8000/api'
    }

    async function testConnection() {
      connectionTest.value = { message: 'Testing...', success: false }
      try {
        const response = await fetch(`${debugInfo.value.apiUrl}/health/`, {
          method: 'GET',
          credentials: 'include',
        })
        if (response.ok) {
          connectionTest.value = { message: 'Connection successful!', success: true }
        } else {
          connectionTest.value = { message: `Connection failed: ${response.status}`, success: false }
        }
      } catch (error) {
        connectionTest.value = { message: `Network error: ${error.message}`, success: false }
      }
    }

    async function handleLogin() {
      try {
        // Get CSRF token first
        await api.getCsrfToken()
        // Then login
        await api.login(username.value, password.value)
        router.push('/whiteboards')
      } catch (error) {
        console.error('Login error:', error)
        alert('Login failed. Please check your credentials.')
      }
    }

    return {
      username,
      password,
      handleLogin,
      debugInfo,
      connectionTest,
      testConnection,
    }
  },
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  min-width: 350px;
}

.login-card h1 {
  margin: 0 0 10px 0;
  text-align: center;
  color: #333;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn {
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.btn-primary {
  background: #4caf50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.info-text {
  margin-top: 20px;
  font-size: 12px;
  color: #666;
  text-align: center;
}

code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.debug-info {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  font-size: 12px;
  text-align: left;
}

.debug-info h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.debug-info p {
  margin: 5px 0;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-top: 10px;
}

.btn-secondary:hover {
  background: #5a6268;
}

.connection-test {
  margin-top: 10px;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
}

.connection-test.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.connection-test.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
