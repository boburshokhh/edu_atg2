<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">
            Управление Hero-слайдером
          </h1>
          <p class="text-gray-600 text-lg">
            Загрузите несколько изображений для создания слайдера на главной странице
          </p>
        </div>
        <el-button @click="$router.push('/admin')">
          <el-icon class="mr-2">
            <ArrowLeft />
          </el-icon>
          Назад
        </el-button>
      </div>

      <el-card v-loading="loading" class="shadow-xl">
        <div class="space-y-8">
          <!-- Upload Section -->
          <div>
            <h2 class="text-xl font-semibold text-gray-800 mb-4">
              Загрузить новые изображения
            </h2>
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              multiple
              class="hidden"
              @change="handleFileInputChange"
            >
            <el-button
              type="primary"
              size="large"
              class="w-full sm:w-auto"
              @click="$refs.fileInputRef.click()"
            >
              <el-icon class="mr-2">
                <Upload />
              </el-icon>
              Выбрать файлы (можно несколько)
            </el-button>

            <div v-if="previewFiles.length > 0" class="mt-4">
              <p class="text-sm text-gray-600 mb-3">
                Предпросмотр новых файлов ({{ previewFiles.length }})
              </p>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div
                  v-for="(file, index) in previewFiles"
                  :key="`preview-${index}`"
                  class="relative group border rounded-lg overflow-hidden bg-gray-50"
                >
                  <img
                    :src="file.preview"
                    alt="Preview"
                    class="w-full h-32 object-cover"
                  >
                  <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <el-button
                      type="danger"
                      size="small"
                      circle
                      @click="removePreviewFile(index)"
                    >
                      <el-icon>
                        <Delete />
                      </el-icon>
                    </el-button>
                  </div>
                  <div class="p-2 text-xs text-gray-600 truncate">
                    {{ file.name }}
                  </div>
                </div>
              </div>
              <div class="mt-4 flex gap-3">
                <el-button
                  type="success"
                  :loading="uploading"
                  :disabled="previewFiles.length === 0"
                  @click="uploadFiles"
                >
                  Загрузить выбранные файлы
                </el-button>
                <el-button
                  :disabled="uploading"
                  @click="clearPreviewFiles"
                >
                  Очистить
                </el-button>
              </div>
            </div>
          </div>

          <!-- Current Slider Images -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-gray-800">
                Текущие слайды ({{ sliderItems.length }})
              </h2>
              <el-button
                v-if="sliderItems.length > 0"
                type="success"
                :loading="saving"
                :disabled="!hasChanges"
                @click="saveSlider"
              >
                Сохранить изменения
              </el-button>
            </div>

            <div v-if="sliderItems.length === 0" class="text-center py-12 text-gray-400">
              <el-icon :size="64" class="mb-4">
                <Picture />
              </el-icon>
              <p>Нет загруженных изображений</p>
              <p class="text-sm mt-2">
                Загрузите изображения выше, чтобы создать слайдер
              </p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="(item, index) in sliderItems"
                :key="item.id || `temp-${index}`"
                class="flex items-center gap-4 p-4 border rounded-lg bg-white hover:shadow-md transition-shadow"
              >
                <!-- Image Preview -->
                <div class="flex-shrink-0 w-32 h-24 border rounded overflow-hidden bg-gray-50">
                  <img
                    v-if="item.url"
                    :src="item.url"
                    alt="Slide"
                    class="w-full h-full object-cover"
                  >
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                    Нет изображения
                  </div>
                </div>

                <!-- Info -->
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ item.key }}
                  </p>
                  <p class="text-xs text-gray-500 mt-1">
                    Порядок: {{ item.orderIndex + 1 }}
                  </p>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2">
                  <el-button
                    size="small"
                    :disabled="index === 0 || saving"
                    circle
                    @click="moveUp(index)"
                  >
                    <el-icon>
                      <ArrowUp />
                    </el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    :disabled="index === sliderItems.length - 1 || saving"
                    circle
                    @click="moveDown(index)"
                  >
                    <el-icon>
                      <ArrowDown />
                    </el-icon>
                  </el-button>
                  <el-popconfirm
                    title="Удалить этот слайд?"
                    @confirm="removeItem(index)"
                  >
                    <template #reference>
                      <el-button
                        type="danger"
                        size="small"
                        :disabled="saving"
                        circle
                      >
                        <el-icon>
                          <Delete />
                        </el-icon>
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Upload, Delete, Picture, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import siteSettingsService from '@/services/siteSettingsService'

const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)

const sliderItems = ref([])
const originalOrder = ref([])

const previewFiles = ref([])

const hasChanges = computed(() => {
  if (sliderItems.value.length !== originalOrder.value.length) return true
  return sliderItems.value.some((item, idx) => item.orderIndex !== originalOrder.value[idx]?.orderIndex)
})

const loadSlider = async () => {
  loading.value = true
  try {
    const data = await siteSettingsService.getHeroSlider()
    sliderItems.value = data.items || []
    originalOrder.value = JSON.parse(JSON.stringify(sliderItems.value))
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка загрузки слайдера')
  } finally {
    loading.value = false
  }
}

const fileInputRef = ref(null)

const handleFileInputChange = (event) => {
  const files = Array.from(event.target.files || [])
  if (files.length === 0) return
  
  // Track existing file names to avoid duplicates
  const existingNames = new Set(previewFiles.value.map(pf => pf.name))
  
  // Add only new files (not already in preview)
  files.forEach(file => {
    // Skip if already in preview
    if (existingNames.has(file.name)) {
      return
    }
    
    if (!String(file.type || '').startsWith('image/')) {
      ElMessage.warning(`Файл ${file.name} не является изображением, пропущен`)
      return
    }
    if (file.size > 20 * 1024 * 1024) {
      ElMessage.warning(`Файл ${file.name} слишком большой (макс 20MB), пропущен`)
      return
    }
    
    previewFiles.value.push({
      file,
      name: file.name,
      preview: URL.createObjectURL(file)
    })
    existingNames.add(file.name)
  })
  
  // Reset input to allow selecting same files again if needed
  event.target.value = ''
}

const removePreviewFile = (index) => {
  if (previewFiles.value[index]?.preview) {
    URL.revokeObjectURL(previewFiles.value[index].preview)
  }
  previewFiles.value.splice(index, 1)
}

const clearPreviewFiles = () => {
  previewFiles.value.forEach(pf => {
    if (pf.preview) URL.revokeObjectURL(pf.preview)
  })
  previewFiles.value = []
}

const uploadFiles = async () => {
  if (previewFiles.value.length === 0) return

  uploading.value = true
  try {
    const files = previewFiles.value.map(pf => pf.file)
    const result = await siteSettingsService.uploadHeroSlides(files)

    if (result.uploaded && result.uploaded.length > 0) {
      ElMessage.success(`Загружено ${result.uploaded.length} файлов`)
      
      // Add to slider items (only new ones, not existing)
      const newItems = result.uploaded.map((item, idx) => ({
        id: null, // Will be assigned by backend after save
        key: item.key,
        url: item.url,
        orderIndex: sliderItems.value.length + idx
      }))
      sliderItems.value.push(...newItems)
      
      // Immediately save the entire list to backend to persist changes
      const keys = sliderItems.value.map(item => item.key)
      await siteSettingsService.setHeroSliderKeys(keys)
      
      // Reload to get proper IDs from backend
      await loadSlider()
      
      clearPreviewFiles()
      ElMessage.success('Слайдер обновлен')
    } else {
      ElMessage.warning('Не удалось загрузить файлы')
    }
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка загрузки файлов')
  } finally {
    uploading.value = false
  }
}

const moveUp = (index) => {
  if (index === 0) return
  const item = sliderItems.value[index]
  sliderItems.value[index] = sliderItems.value[index - 1]
  sliderItems.value[index - 1] = item
  // Update order indices
  sliderItems.value.forEach((it, idx) => {
    it.orderIndex = idx
  })
}

const moveDown = (index) => {
  if (index === sliderItems.value.length - 1) return
  const item = sliderItems.value[index]
  sliderItems.value[index] = sliderItems.value[index + 1]
  sliderItems.value[index + 1] = item
  // Update order indices
  sliderItems.value.forEach((it, idx) => {
    it.orderIndex = idx
  })
}

const removeItem = (index) => {
  sliderItems.value.splice(index, 1)
  // Update order indices
  sliderItems.value.forEach((it, idx) => {
    it.orderIndex = idx
  })
}

const saveSlider = async () => {
  if (sliderItems.value.length === 0) {
    ElMessage.warning('Нет слайдов для сохранения')
    return
  }

  saving.value = true
  try {
    const keys = sliderItems.value.map(item => item.key)
    await siteSettingsService.setHeroSliderKeys(keys)
    ElMessage.success('Слайдер сохранен')
    await loadSlider()
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка сохранения слайдера')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSlider()
})

onUnmounted(() => {
  previewFiles.value.forEach(pf => {
    if (pf.preview) URL.revokeObjectURL(pf.preview)
  })
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
