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
              Загрузить изображения из папки public/slider
            </h2>
            <div class="mb-4">
              <el-button
                type="success"
                size="large"
                :loading="loadingFromPublic"
                @click="loadFromPublicFolder"
              >
                <el-icon class="mr-2">
                  <FolderOpened />
                </el-icon>
                Загрузить из public/slider
              </el-button>
              <p class="text-sm text-gray-500 mt-2">
                Загрузит все изображения из папки public/slider в слайдер
              </p>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Picture, ArrowUp, ArrowDown, FolderOpened } from '@element-plus/icons-vue'
import siteSettingsService from '@/services/siteSettingsService'
import { deleteFile } from '@/services/minioService'

const loading = ref(false)
const saving = ref(false)
const loadingFromPublic = ref(false)

const sliderItems = ref([])
const originalOrder = ref([])

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

const removeItem = async (index) => {
  const item = sliderItems.value[index]
  if (!item) return
  
  try {
    await ElMessageBox.confirm(
      'Вы уверены, что хотите удалить этот слайд? Файл будет удален из хранилища.',
      'Подтверждение удаления',
      {
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена',
        type: 'warning'
      }
    )

    const itemKey = item.key
    
    // Удаляем из массива
    sliderItems.value.splice(index, 1)
    // Update order indices
    sliderItems.value.forEach((it, idx) => {
      it.orderIndex = idx
    })
    
    // Удаляем файл из MinIO, если есть key
    if (itemKey && !itemKey.startsWith('http')) {
      try {
        await deleteFile(itemKey)
      } catch (fileError) {
        console.warn('Не удалось удалить файл из MinIO:', fileError)
        // Продолжаем, даже если удаление файла не удалось
      }
    }
    
    ElMessage.success('Слайд удален')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }
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

const loadFromPublicFolder = async () => {
  loadingFromPublic.value = true
  try {
    const result = await siteSettingsService.loadHeroSlidesFromPublic()
    
    if (result.uploaded && result.uploaded.length > 0) {
      ElMessage.success(`Загружено ${result.count} файлов из public/slider`)
      
      // Add to slider items
      const newItems = result.uploaded.map((item, idx) => ({
        id: null, // Will be assigned by backend after save
        key: item.key,
        url: item.url,
        orderIndex: sliderItems.value.length + idx
      }))
      sliderItems.value.push(...newItems)
      
      // Immediately save the entire list to backend
      const keys = sliderItems.value.map(item => item.key)
      await siteSettingsService.setHeroSliderKeys(keys)
      
      // Reload to get proper IDs from backend
      await loadSlider()
      
      ElMessage.success('Слайдер обновлен')
    } else {
      ElMessage.warning('Не удалось загрузить файлы из public/slider')
    }
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка загрузки файлов из public/slider')
  } finally {
    loadingFromPublic.value = false
  }
}

onMounted(() => {
  loadSlider()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
