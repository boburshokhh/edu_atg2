<template>
  <div class="flex items-center mb-6">
    <el-button
      class="mr-4"
      @click="$router.push('/admin')"
    >
      <el-icon class="mr-2">
        <ArrowLeft />
      </el-icon>
      Назад
    </el-button>
    <h1 class="text-2xl font-bold text-gray-800">
      {{ isEditing ? `Редактирование станции: ${stationName || 'Загрузка...'}` : 'Новая станция' }}
    </h1>
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'

defineProps({
  isEditing: {
    type: Boolean,
    required: true
  },
  stationName: {
    type: String,
    default: ''
  }
})
</script>

