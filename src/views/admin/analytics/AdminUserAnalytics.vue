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
          <el-avatar :src="user.avatar_url" :size="48">
            {{ (user.full_name || user.username || 'U').charAt(0) }}
          </el-avatar>
          <div class="flex-1">
            <div class="font-semibold text-gray-900">{{ user.full_name || user.username }}</div>
            <div class="text-xs text-gray-500">{{ user.email }}</div>
            <div class="text-xs text-gray-400">{{ user.position || 'Должность не указана' }}</div>
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

const users = ref([])
const search = ref('')

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
