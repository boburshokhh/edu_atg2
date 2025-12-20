<template>
  <el-header class="lesson-header">
    <div class="lesson-header-content">
      <div class="lesson-header-left">
        <!-- Breadcrumb -->
        <el-breadcrumb separator="/" class="lesson-breadcrumb">
          <el-breadcrumb-item :to="{ path: '/stations' }">
            <span>Станции</span>
          </el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: `/station/${stationId}` }">
            <span>{{ station?.shortName }}</span>
          </el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: `/station/${stationId}/courses` }">
            <span>Программа</span>
          </el-breadcrumb-item>
          <el-breadcrumb-item>
            <span class="lesson-title-truncate">{{ currentLesson?.title }}</span>
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <!-- User Account Section -->
      <div class="lesson-header-right">
        <template v-if="!isAuthenticated">
          <el-button 
            type="primary" 
            plain
            @click="$router.push('/login')"
          >
            Войти
          </el-button>
        </template>

        <template v-else>
          <el-dropdown 
            trigger="click"
            placement="bottom-end"
            @command="handleCommand"
          >
            <div class="user-menu-trigger">
              <el-avatar 
                :src="userAvatar" 
                :size="40"
                class="user-avatar"
              >
                <span class="avatar-text">{{ userName.charAt(0).toUpperCase() }}</span>
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ userName }}</div>
                <div class="user-role">{{ userRole }}</div>
              </div>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>Профиль</span>
                </el-dropdown-item>
                <el-dropdown-item command="rating">
                  <el-icon><DataLine /></el-icon>
                  <span>Рейтинг</span>
                </el-dropdown-item>
                <el-dropdown-item 
                  v-if="isAdminUser"
                  command="admin"
                  divided
                >
                  <el-icon><Setting /></el-icon>
                  <span>Админ-панель</span>
                </el-dropdown-item>
                <el-dropdown-item 
                  command="logout"
                  divided
                  class="logout-item"
                >
                  <el-icon><SwitchButton /></el-icon>
                  <span>Выйти</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </div>
    </div>
  </el-header>

  <!-- Drawer для статистики -->
  <el-drawer
    v-model="showStatistics"
    title="Моя статистика"
    direction="rtl"
    size="50%"
    :with-header="true"
    custom-class="statistics-drawer"
  >
    <div class="h-full overflow-y-auto p-2">
      <UserStatistics />
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, User, Setting, SwitchButton, Monitor, DataLine } from '@element-plus/icons-vue'
import authService from '@/services/auth'
import userProfileService from '@/services/userProfile'
import UserStatistics from '@/components/UserStatistics.vue'

const props = defineProps({
  stationId: {
    type: Number,
    required: true
  },
  station: {
    type: Object,
    default: () => ({})
  },
  currentLesson: {
    type: Object,
    default: () => ({})
  }
})

const router = useRouter()

// Ref для принудительного обновления computed свойств
const userDataVersion = ref(0)
const showStatistics = ref(false) // Для управления Drawer

// Функция для обновления данных пользователя
const refreshUserData = async () => {
  authService.refreshUser()
  const currentUser = authService.getCurrentUser()
  
  if (currentUser?.id) {
    try {
      const profileResult = await userProfileService.getProfile(currentUser.id)
      if (profileResult.success && profileResult.data) {
        const profileData = profileResult.data
        
        // Обновляем данные в authService
        if (authService.currentUser) {
          const updatedUser = {
            ...authService.currentUser,
            full_name: profileData.full_name || authService.currentUser.full_name,
            role: profileData.role || authService.currentUser.role,
            avatar_url: profileData.avatar_url || authService.currentUser.avatar_url || null,
            position: profileData.position || authService.currentUser.position || null,
            station: profileData.station || profileData.company || authService.currentUser.station || null // Маппинг company -> station
          }
          
          authService.currentUser = updatedUser
          // Сохраняем в localStorage
          localStorage.setItem('user', JSON.stringify(updatedUser))
        }
      }
    } catch (error) {
      console.error('Error loading user profile:', error)
    }
  }
  userDataVersion.value++ // Принудительно обновляем computed свойства
}

const mockUser = {
  full_name: 'Отабек Нуриддинов',
  role: 'user',
  avatar_url: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80'
}

const isAuthenticated = computed(() => {
  userDataVersion.value // Зависимость для обновления
  return authService.getCurrentUser() !== null
})

const userName = computed(() => {
  userDataVersion.value // Зависимость для обновления
  const user = authService.getCurrentUser()
  
  if (user) {
    return user.full_name || user.username || 'Пользователь'
  }
  
  return mockUser.full_name
})

const userAvatar = computed(() => {
  userDataVersion.value // Зависимость для обновления
  const user = authService.getCurrentUser()
  
  if (user) {
    return user.avatar_url || user.avatar || null
  }
  
  return mockUser.avatar_url
})

const userRole = computed(() => {
  userDataVersion.value // Зависимость для обновления
  const user = authService.getCurrentUser()
  
  const role = user ? user.role : mockUser.role
  
  const roles = {
    admin: 'Администратор',
    instructor: 'Инструктор',
    user: 'Студент'
  }
  return roles[role] || 'Студент'
})

const isAdminUser = computed(() => {
  userDataVersion.value // Зависимость для обновления
  return authService.isAdmin()
})

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'rating':
      showStatistics.value = true
      break
    case 'admin':
      router.push('/admin/stations')
      break
    case 'logout':
      await logout()
      break
  }
}

const logout = async () => {
  try {
    const result = await authService.logout()
    
    if (result.success) {
      router.push('/').then(() => {
        window.location.href = '/'
      })
    } else {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
  } catch (error) {
    console.error('Logout error:', error)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    window.location.href = '/'
  }
}

// Обработчик обновления профиля
const handleProfileUpdate = () => {
  refreshUserData()
}

onMounted(async () => {
  // Слушаем обновления профиля
  window.addEventListener('user-profile-updated', handleProfileUpdate)
  // Загружаем данные пользователя при монтировании
  await refreshUserData()
})

onUnmounted(() => {
  window.removeEventListener('user-profile-updated', handleProfileUpdate)
})
</script>

<style scoped>
:deep(.statistics-drawer .el-drawer__body) {
  padding: 0;
  background-color: #f9fafb;
}
:deep(.statistics-drawer .el-drawer__header) {
  margin-bottom: 0;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.lesson-header {
  height: auto !important;
  padding: 0 !important;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
  width: 100%;
  max-width: 100%;
}

.lesson-header-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: clamp(0.5rem, 1.5vw, 0.75rem) clamp(0.75rem, 2vw, 1rem);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(0.5rem, 1.5vw, 1rem);
  flex-wrap: wrap;
  width: 100%;
}

.lesson-header-left {
  flex: 1;
  min-width: 0;
  width: 100%;
  max-width: 100%;
}

.lesson-header-right {
  flex-shrink: 0;
}

.lesson-breadcrumb {
  margin: 0;
  width: 100%;
  max-width: 100%;
}

:deep(.el-breadcrumb__inner) {
  font-size: clamp(0.625rem, 1.5vw, 0.75rem);
  color: #6b7280;
  transition: color 0.2s;
}

:deep(.el-breadcrumb__inner:hover) {
  color: #2563eb;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #1f2937;
  font-weight: 500;
}

.lesson-title-truncate {
  display: inline-block;
  max-width: clamp(8rem, 30vw, 12.5rem);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* User Menu Styles */
.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 1.5vw, 0.75rem);
  padding: clamp(0.25rem, 0.5vw, 0.5rem) clamp(0.5rem, 1vw, 0.75rem);
  border-radius: clamp(0.375rem, 1vw, 0.5rem);
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
  max-width: 100%;
}

.user-menu-trigger:hover {
  background-color: #f3f4f6;
}

.user-avatar {
  flex-shrink: 0;
  width: clamp(2rem, 5vw, 2.5rem);
  height: clamp(2rem, 5vw, 2.5rem);
}

:deep(.user-avatar .el-avatar) {
  width: clamp(2rem, 5vw, 2.5rem) !important;
  height: clamp(2rem, 5vw, 2.5rem) !important;
}

.avatar-text {
  font-weight: 600;
  color: #ffffff;
  font-size: clamp(0.75rem, 2vw, 0.875rem);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
  flex: 1;
}

.user-name {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  font-weight: 500;
  color: #111827;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: clamp(6rem, 20vw, 10rem);
}

.user-role {
  font-size: clamp(0.625rem, 1.5vw, 0.75rem);
  color: #6b7280;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: clamp(6rem, 20vw, 10rem);
}

.dropdown-icon {
  color: #6b7280;
  transition: transform 0.2s;
  flex-shrink: 0;
  font-size: clamp(0.75rem, 2vw, 1rem);
}

:deep(.el-dropdown.is-active .dropdown-icon) {
  transform: rotate(180deg);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 1vw, 0.75rem);
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  padding: clamp(0.5rem, 1.5vw, 0.75rem) clamp(0.75rem, 2vw, 1rem);
}

:deep(.logout-item) {
  color: #ef4444;
}

:deep(.logout-item:hover) {
  background-color: #fef2f2;
  color: #dc2626;
}

/* Media Queries */
/* Mobile phones (max-width: 480px) */
@media (max-width: 480px) {
  .lesson-header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: clamp(0.5rem, 2vw, 0.75rem);
  }

  .lesson-header-left {
    width: 100%;
  }

  .lesson-header-right {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }

  .lesson-title-truncate {
    max-width: clamp(10rem, 50vw, 15rem);
  }

  .user-info {
    display: none;
  }

  .user-menu-trigger {
    gap: clamp(0.25rem, 1vw, 0.5rem);
  }
}

/* Tablets (max-width: 768px) */
@media (max-width: 768px) {
  .lesson-header-content {
    flex-wrap: wrap;
  }

  .user-name,
  .user-role {
    max-width: clamp(5rem, 15vw, 8rem);
  }
}

/* Small laptops (max-width: 1024px) */
@media (max-width: 1024px) {
  .lesson-header-content {
    padding: clamp(0.5rem, 1.5vw, 0.75rem) clamp(0.75rem, 2vw, 1rem);
  }
}

/* Desktop (min-width: 1025px) */
@media (min-width: 1025px) {
  .lesson-header-content {
    flex-wrap: nowrap;
  }

  .user-info {
    display: flex;
  }
}

/* Wide monitors (min-width: 1440px) */
@media (min-width: 1440px) {
  .lesson-header-content {
    max-width: 1920px;
  }

  .lesson-title-truncate {
    max-width: 12.5rem;
  }

  .user-name,
  .user-role {
    max-width: 10rem;
  }
}
</style>


