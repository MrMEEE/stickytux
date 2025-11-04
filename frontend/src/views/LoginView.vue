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
</style>
