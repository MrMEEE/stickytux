import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import WhiteboardsView from '../views/WhiteboardsView.vue'
import WhiteboardView from '../views/WhiteboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/whiteboards',
      name: 'whiteboards',
      component: WhiteboardsView,
    },
    {
      path: '/whiteboard/:id',
      name: 'whiteboard',
      component: WhiteboardView,
    },
  ],
})

export default router

