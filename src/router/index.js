import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Home from '@/views/public/Home.vue'
import Courses from '@/views/course/Courses.vue'
import CourseDetail from '@/views/course/CourseDetail.vue'
import Stations from '@/views/station/Stations.vue'
import StationDetail from '@/views/station/StationDetail.vue'
import StationCourses from '@/views/station/StationCourses.vue'
import Departments from '@/components/Departments.vue'
import LessonViewer from '@/views/lesson/LessonViewer.vue'
import Profile from '@/views/user/Profile.vue'
import Login from '@/views/public/Login.vue'
import Dashboard from '@/views/user/Dashboard.vue'
import StationList from '@/views/admin/StationList.vue'
import StationEditor from '@/views/admin/StationEditor.vue'
import DepartmentList from '@/views/admin/DepartmentList.vue'
import DepartmentEditor from '@/views/admin/DepartmentEditor.vue'
import AdminHome from '@/views/admin/AdminHome.vue'
import RegisterProfile from '@/views/user/RegisterProfile.vue'
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
    path: '/departments',
    name: 'Departments',
    component: Departments
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
    meta: { requiresAuth: true, hideHeader: true, hideFooter: true }
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
    component: Login,
    meta: { hideHeader: true, hideFooter: true }
  },
  {
    path: '/register',
    name: 'RegisterProfile',
    component: RegisterProfile,
    meta: { requiresAuth: true }
  },
  // Admin Routes
  {
    path: '/admin',
    name: 'AdminHome',
    component: AdminHome,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
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
  {
    path: '/admin/departments',
    name: 'AdminDepartments',
    component: DepartmentList,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/departments/new',
    name: 'AdminDepartmentCreate',
    component: DepartmentEditor,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/departments/:id',
    name: 'AdminDepartmentEdit',
    component: DepartmentEditor,
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
  } else if (to.path === '/register' && authResult.isAuthenticated) {
    // Не показываем страницу регистрации повторно, если профиль уже заполнен
    try {
      const token = localStorage.getItem('auth_token')
      if (token) {
        const resp = await fetch('/api/auth/register-profile', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        })
        if (resp.ok) {
          const data = await resp.json()
          if (data && data.profile_complete) {
            if (authService.isInstructor()) {
              next('/dashboard')
            } else {
              next('/profile')
            }
            return
          }
        }
      }
    } catch (e) {
      // Если проверка не удалась, просто показываем страницу регистрации
    }
    next()
  } else if (to.meta.requiresAdmin && !authService.isAdmin()) {
    // Требуются права администратора, но их нет
    ElMessage.error('Доступ запрещен. Требуются права администратора.')
    next('/dashboard')
  } else if (to.path === '/login' && authResult.isAuthenticated) {
    // Пользователь уже авторизован, перенаправляем в зависимости от роли
    if (authService.isInstructor()) {
      next('/dashboard')
    } else {
      // Обычные пользователи попадают в личный кабинет
      next('/profile')
    }
  } else {
    next()
  }
})

export default router
