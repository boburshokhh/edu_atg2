<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Настройки Hero</h1>
        <p class="text-sm text-gray-500">Фоновое изображение на главной странице</p>
      </div>
      <el-button @click="$router.push('/admin/stations')">
        Назад
      </el-button>
    </div>

    <el-card v-loading="loading" class="max-w-4xl">
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-semibold text-gray-800 mb-2">Текущее изображение</h2>
          <div class="border rounded-lg overflow-hidden bg-gray-50">
            <img
              v-if="currentUrl"
              :src="currentUrl"
              alt="Hero background"
              class="w-full h-64 object-cover"
            >
            <div v-else class="h-64 flex items-center justify-center text-gray-400">
              Изображение не установлено
            </div>
          </div>
        </div>

        <div>
          <h2 class="text-lg font-semibold text-gray-800 mb-2">Загрузить новое</h2>
          <div class="flex flex-col gap-4">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              :on-change="handleFileChange"
            >
              <el-button type="primary">Выбрать файл</el-button>
            </el-upload>

            <div v-if="previewUrl" class="space-y-2">
              <div class="text-sm text-gray-600">Предпросмотр</div>
              <div class="border rounded-lg overflow-hidden bg-gray-50">
                <img :src="previewUrl" alt="Preview" class="w-full h-64 object-cover">
              </div>
            </div>

            <div class="flex items-center gap-3">
              <el-button
                type="success"
                :disabled="!selectedFile || saving"
                :loading="saving"
                @click="save"
              >
                Сохранить
              </el-button>
              <el-button
                :disabled="!selectedFile || saving"
                @click="resetSelection"
              >
                Сбросить
              </el-button>
              <div v-if="selectedFile" class="text-sm text-gray-500">
                {{ selectedFile.name }} ({{ formatBytes(selectedFile.size) }})
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import siteSettingsService from '@/services/siteSettingsService'

const loading = ref(false)
const saving = ref(false)

const currentUrl = ref(null)
const currentKey = ref(null)

const selectedFile = ref(null)
const previewUrl = ref(null)

const load = async () => {
  loading.value = true
  try {
    const data = await siteSettingsService.getHeroImage()
    currentKey.value = data.image_key
    currentUrl.value = data.url
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка загрузки настроек')
  } finally {
    loading.value = false
  }
}

const handleFileChange = (uploadFile) => {
  const file = uploadFile?.raw
  if (!file) return
  if (!String(file.type || '').startsWith('image/')) {
    ElMessage.error('Можно загрузить только изображение')
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('Файл слишком большой (макс 20MB)')
    return
  }

  selectedFile.value = file
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)
}

const resetSelection = () => {
  selectedFile.value = null
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
}

const save = async () => {
  if (!selectedFile.value) return
  saving.value = true
  try {
    await siteSettingsService.updateHeroImage(selectedFile.value)
    ElMessage.success('Сохранено')
    resetSelection()
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

const formatBytes = (bytes) => {
  if (!bytes && bytes !== 0) return ''
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = bytes === 0 ? 0 : Math.floor(Math.log(bytes) / Math.log(1024))
  const value = bytes / Math.pow(1024, i)
  return `${value.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`
}

onMounted(load)
onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>


