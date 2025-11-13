<template>
  <el-header class="lesson-header">
    <div class="lesson-header-content">
      <div class="lesson-header-left">
        <!-- Breadcrumb -->
        <el-breadcrumb separator="/" class="lesson-breadcrumb">
          <el-breadcrumb-item :to="{ name: 'Stations' }">
            Станции
          </el-breadcrumb-item>
          <el-breadcrumb-item :to="{ name: 'StationCourses', params: { id: stationId } }">
            {{ station?.name || 'Курсы' }}
          </el-breadcrumb-item>
          <el-breadcrumb-item v-if="currentLesson">
            {{ currentLesson.title }}
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
                  <el-icon><User /></el-icon><span>Профиль</span>
                </el-dropdown-item>
                <el-dropdown-item command="dashboard">
                  <el-icon><Monitor /></el-icon><span>Панель управления</span>
                </el-dropdown-item>
                <el-dropdown-item 
                  v-if="isAdminUser"
                  command="admin"
                  divided
                >
                  <el-icon><Setting /></el-icon><span>Админ-панель</span>
                </el-dropdown-item>
                <el-dropdown-item 
                  command="logout"
                  divided
                  class="logout-item"
                >
                  <el-icon><SwitchButton /></el-icon><span>Выйти</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, User, Setting, SwitchButton, Monitor } from '@element-plus/icons-vue'
import authService from '@/services/auth'

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
    default: null
  }
})

const router = useRouter()

const isAuthenticated = computed(() => {
  return authService.getCurrentUser() !== null
})

const userName = computed(() => {
  const user = authService.getCurrentUser()
  return user ? (user.full_name || user.username || 'Пользователь') : 'Пользователь'
})

const userAvatar = computed(() => {
  const user = authService.getCurrentUser()
  return user?.avatar_url || user?.avatar || ''
})

const userRole = computed(() => {
  const user = authService.getCurrentUser()
  if (!user) return ''
  const roles = {
    admin: 'Администратор',
    instructor: 'Инструктор',
    user: 'Пользователь'
  }
  return roles[user.role] || 'Пользователь'
})

const isAdminUser = computed(() => {
  return authService.isAdmin()
})

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'dashboard':
      router.push('/dashboard')
      break
    case 'admin':
      router.push('/admin')
      break
    case 'logout':
      try {
        await authService.logout()
        ElMessage.success('Вы успешно вышли из системы')
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        ElMessage.error('Ошибка при выходе из системы')
      }
      break
  }
}
</script>

<style scoped>
.lesson-header {
  height: auto !important;
  padding: 0 !important;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
}

.lesson-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  min-height: 64px;
}

.lesson-header-left {
  flex: 1;
  min-width: 0;
}

.lesson-header-right {
  flex-shrink: 0;
  margin-left: 16px;
}

.lesson-breadcrumb {
  font-size: 14px;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-menu-trigger:hover {
  background-color: #f3f4f6;
}

.user-avatar {
  flex-shrink: 0;
}

.avatar-text {
  font-weight: 600;
  color: #ffffff;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.2;
}

.dropdown-icon {
  color: #6b7280;
  transition: transform 0.2s;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item.logout-item) {
  color: #ef4444;
}

:deep(.el-dropdown-menu__item.logout-item:hover) {
  background-color: #fef2f2;
  color: #dc2626;
}

@media (max-width: 768px) {
  .lesson-header-content {
    padding: 8px 12px;
    min-height: 56px;
  }

  .user-info {
    display: none;
  }

  .lesson-breadcrumb {
    font-size: 12px;
  }
}
</style>
