<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <el-input v-model="search" placeholder="Поиск пользователя" clearable class="max-w-md" />
      <el-tag type="info">{{ filteredUsers.length }} пользователей</el-tag>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <el-card
        v-for="user in filteredUsers"
        :key="user.user_id"
        shadow="hover"
        class="cursor-pointer"
        @click="$router.push(`/admin/analytics/users/${user.user_id}`)"
      >
        <div class="flex items-center gap-3">
          <div 
            class="w-12 h-12 rounded-full overflow-hidden ring-2 ring-offset-2 transition-all hover:ring-offset-4 shrink-0"
            :class="getAvatarUrl(user) && !imageErrors[user.user_id]
              ? 'ring-blue-500' 
              : 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-300'"
          >
            <img 
              v-if="getAvatarUrl(user) && !imageErrors[user.user_id]" 
              :src="getAvatarUrl(user)" 
              :alt="user.full_name || user.username"
              class="w-full h-full object-cover transition-transform duration-300"
              @error="() => handleImageError(user.user_id)"
            >
            <div
              v-else
              class="w-full h-full flex items-center justify-center text-white text-sm font-semibold"
            >
              {{ (user.full_name || user.username || 'U').charAt(0).toUpperCase() }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-semibold text-gray-900 truncate">{{ user.full_name || user.username }}</div>
            <div class="text-xs text-gray-500 truncate">{{ user.email }}</div>
            <div class="text-xs text-gray-400 truncate">{{ user.position || 'Должность не указана' }}</div>
          </div>
        </div>
        <div class="mt-4 space-y-2">
          <div class="flex justify-between text-xs text-gray-500">
            <span>Активных курсов</span>
            <span class="font-medium text-gray-700">{{ user.active_courses }}</span>
          </div>
          <el-progress :percentage="user.average_progress || 0" :stroke-width="8" :show-text="false" />
          <div class="flex justify-between text-xs text-gray-500">
            <span>Средний балл</span>
            <span class="font-medium text-gray-700">{{ user.average_test_score || 0 }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import adminAnalyticsService from '@/services/adminAnalyticsService'
import { getFrontendUrl } from '@/services/minioService'

const users = ref([])
const search = ref('')
const imageErrors = ref({})

const getAvatarUrl = (user) => {
  if (!user.avatar_url) return null
  try {
    return getFrontendUrl(user.avatar_url)
  } catch {
    return user.avatar_url
  }
}

const handleImageError = (userId) => {
  imageErrors.value[userId] = true
}

const filteredUsers = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return users.value
  return users.value.filter(user =>
    (user.full_name || '').toLowerCase().includes(query) ||
    (user.username || '').toLowerCase().includes(query) ||
    (user.email || '').toLowerCase().includes(query)
  )
})

onMounted(async () => {
  users.value = await adminAnalyticsService.getUsersAnalytics()
})
</script>
