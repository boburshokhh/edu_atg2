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
import StationList from '@/views/admin/StationList.vue'
import StationEditor from '@/views/admin/StationEditor.vue'
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
    path: '/register',
    name: 'RegisterProfile',
    component: () => import('@/views/RegisterProfile.vue'),
    meta: { requiresAuth: true }
  },
  // Admin Routes
  {
    path: '/admin/stations',
    name: 'AdminStations',
    component: StationList,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/stations/new',
    name: 'AdminStationCreate',
    component: StationEditor,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/stations/:id',
    name: 'AdminStationEdit',
    component: StationEditor,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
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
  // Проверяем авторизацию
  const authResult = await authService.checkAuth()
  
  if (to.meta.requiresAuth && !authResult.isAuthenticated) {
    // Пользователь не авторизован, перенаправляем на страницу входа
    next('/login')
  } else if (to.meta.requiresAdmin && !authService.isAdmin()) {
    // Требуются права администратора, но их нет
    ElMessage.error('Доступ запрещен. Требуются права администратора.')
    next('/dashboard')
  } else if (to.path === '/login' && authResult.isAuthenticated) {
    // Пользователь уже авторизован, перенаправляем в зависимости от роли
    if (authService.isInstructor()) {
      next('/dashboard')
    } else {
      // Обычные пользователи попадают сразу на первый урок первой станции
      next('/station/1/lesson/0/0')
    }
  } else {
    next()
  }
})

export default router
