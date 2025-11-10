import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Home from '@/views/Home.vue'
import Courses from '@/views/Courses.vue'
import CourseDetail from '@/views/CourseDetail.vue'
import Stations from '@/views/Stations.vue'
import StationDetail from '@/views/StationDetail.vue'
import StationCourses from '@/views/StationCourses.vue'
import LessonViewer from '@/views/LessonViewer.vue'
import Profile from '@/views/Profile.vue'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import authService from '@/services/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/courses',
    name: 'Courses',
    component: Courses
  },
  {
    path: '/course/:id',
    name: 'CourseDetail',
    component: CourseDetail,
    props: true
  },
  {
    path: '/stations',
    name: 'Stations',
    component: Stations
  },
  {
    path: '/station/:id',
    name: 'StationDetail',
    component: StationDetail,
    props: true
  },
  {
    path: '/station/:id/courses',
    name: 'StationCourses',
    component: StationCourses,
    props: true
  },
  {
    path: '/station/:id/lesson/:lessonIndex/:topicIndex',
    name: 'lesson-viewer',
    component: LessonViewer,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: () => import('@/views/AdminPanel.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Навигационные хуки для проверки авторизации
router.beforeEach(async (to, from, next) => {
  // Проверяем авторизацию через Supabase
  const authResult = await authService.checkAuth()
  
  if (to.meta.requiresAuth && !authResult.isAuthenticated) {
    // Пользователь не авторизован, перенаправляем на страницу входа
    next('/login')
  } else if (to.meta.requiresAdmin && !authService.isAdmin()) {
    // Требуется доступ администратора
    ElMessage.error('У вас нет доступа к этой странице')
    next('/dashboard')
  } else if (to.path === '/login' && authResult.isAuthenticated) {
    // Пользователь уже авторизован, перенаправляем на дашборд
    next('/dashboard')
  } else {
    next()
  }
})

export default router
