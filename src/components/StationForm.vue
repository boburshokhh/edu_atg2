<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? 'Редактировать станцию' : 'Создать станцию'"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="180px"
      label-position="left"
    >
      <el-tabs v-model="activeTab" type="border-card">
        <!-- Основная информация -->
        <el-tab-pane label="Основная информация" name="basic">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Название" prop="name">
                <el-input v-model="formData.name" placeholder="Введите название станции" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Короткое название" prop="shortName">
                <el-input v-model="formData.shortName" placeholder="WKC1, WKC2, etc." />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Описание" prop="description">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="3"
              placeholder="Введите описание станции"
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Изображение станции">
                <div class="flex flex-col gap-2">
                  <!-- Always show el-upload, it will handle empty state -->
                  <el-upload
                    ref="imageUploadRef"
                    action="#"
                    :auto-upload="false"
                    :on-change="handleImageChange"
                    :on-remove="handleImageRemove"
                    :file-list="imageFileList"
                    :limit="1"
                    accept="image/*"
                    list-type="picture-card"
                    :before-upload="() => false"
                    class="upload-image"
                  >
                    <template #default>
                      <el-icon class="upload-icon"><Plus /></el-icon>
                      <div class="upload-text">Нажмите для загрузки</div>
                    </template>
                  </el-upload>
                  <el-input 
                    v-model="formData.image" 
                    placeholder="Или введите путь к изображению (например: stations/WKC1.jpg)"
                    clearable
                  />
                  <div v-if="formData.image && !imageFileList.length" class="mt-2">
                    <img 
                      v-if="isImageUrl(formData.image)" 
                      :src="imagePreviewUrl" 
                      alt="Preview" 
                      class="max-w-full h-32 object-cover rounded"
                      @error="handleImageError"
                    />
                  </div>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Техническая карта">
                <div class="flex flex-col gap-2">
                  <!-- Always show el-upload, it will handle empty state -->
                  <el-upload
                    ref="techMapUploadRef"
                    action="#"
                    :auto-upload="false"
                    :on-change="handleTechMapChange"
                    :on-remove="handleTechMapRemove"
                    :file-list="techMapFileList"
                    :limit="1"
                    accept="image/*"
                    list-type="picture-card"
                    :before-upload="() => false"
                    class="upload-image"
                  >
                    <template #default>
                      <el-icon class="upload-icon"><Plus /></el-icon>
                      <div class="upload-text">Нажмите для загрузки</div>
                    </template>
                  </el-upload>
                  <el-input 
                    v-model="formData.techMapImage" 
                    placeholder="Или введите путь (например: /tex_kart/КС1.jpg)"
                    clearable
                  />
                  <div v-if="formData.techMapImage && !techMapFileList.length" class="mt-2">
                    <img 
                      v-if="isImageUrl(formData.techMapImage)" 
                      :src="techMapPreviewUrl" 
                      alt="Tech Map Preview" 
                      class="max-w-full h-32 object-cover rounded"
                      @error="handleImageError"
                    />
                  </div>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Мощность">
                <el-input v-model="formData.power" placeholder="30 МВт" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Дата ввода в эксплуатацию">
                <el-input v-model="formData.commissionDate" placeholder="2009" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Местоположение">
            <el-input
              v-model="formData.location"
              type="textarea"
              :rows="2"
              placeholder="Введите местоположение"
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Тип станции">
                <el-input v-model="formData.type" placeholder="Тип станции" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Статус" prop="status">
                <el-select v-model="formData.status" placeholder="Выберите статус">
                  <el-option label="Активна" value="active" />
                  <el-option label="На обслуживании" value="maintenance" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Проектная мощность">
                <el-input v-model="formData.designCapacity" placeholder="30 млрд м³/год" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Давление газа">
                <el-input v-model="formData.gasPressure" placeholder="7.0 МПа" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Расстояние от границы">
                <el-input v-model="formData.distanceFromBorder" placeholder="10.6 км" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Диаметр трубопровода">
                <el-input v-model="formData.pipelineDiameter" placeholder="1067 мм" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Входное давление">
                <el-input v-model="formData.inputPressure" placeholder="7.0 МПа" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Выходное давление">
                <el-input v-model="formData.outputPressure" placeholder="9.81 МПа" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Параллельные линии">
            <el-input v-model="formData.parallelLines" placeholder="Две нитки (А, В)" />
          </el-form-item>
        </el-tab-pane>

        <!-- Оборудование -->
        <el-tab-pane label="Оборудование" name="equipment">
          <div class="mb-4">
            <el-button type="primary" @click="addEquipment">
              <el-icon><Plus /></el-icon>
              Добавить оборудование
            </el-button>
          </div>
          <el-table :data="formData.equipment" border>
            <el-table-column prop="name" label="Название" width="200">
              <template #default="{ row, $index }">
                <el-input v-model="row.name" placeholder="Название" />
              </template>
            </el-table-column>
            <el-table-column prop="model" label="Модель" width="200">
              <template #default="{ row }">
                <el-input v-model="row.model" placeholder="Модель" />
              </template>
            </el-table-column>
            <el-table-column prop="manufacturer" label="Производитель" width="200">
              <template #default="{ row }">
                <el-input v-model="row.manufacturer" placeholder="Производитель" />
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="Количество" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" />
              </template>
            </el-table-column>
            <el-table-column prop="power" label="Мощность" width="150">
              <template #default="{ row }">
                <el-input v-model="row.power" placeholder="Мощность" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Описание">
              <template #default="{ row }">
                <el-input v-model="row.description" type="textarea" :rows="2" placeholder="Описание" />
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="100" fixed="right">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeEquipment($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Спецификации -->
        <el-tab-pane label="Спецификации" name="specifications">
          <div class="mb-4">
            <el-button type="primary" @click="addSpecification">
              <el-icon><Plus /></el-icon>
              Добавить спецификацию
            </el-button>
          </div>
          <el-table :data="formData.specifications" border>
            <el-table-column prop="category" label="Категория" width="200">
              <template #default="{ row }">
                <el-input v-model="row.category" placeholder="Категория" />
              </template>
            </el-table-column>
            <el-table-column prop="value" label="Значение" width="150">
              <template #default="{ row }">
                <el-input v-model="row.value" placeholder="Значение" />
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="Единица" width="120">
              <template #default="{ row }">
                <el-input v-model="row.unit" placeholder="Единица" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Описание">
              <template #default="{ row }">
                <el-input v-model="row.description" type="textarea" :rows="2" placeholder="Описание" />
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="100" fixed="right">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeSpecification($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Системы безопасности -->
        <el-tab-pane label="Системы безопасности" name="safety">
          <div class="mb-4">
            <el-button type="primary" @click="addSafetySystem">
              <el-icon><Plus /></el-icon>
              Добавить систему безопасности
            </el-button>
          </div>
          <el-table :data="formData.safetySystems" border>
            <el-table-column prop="name" label="Название" width="250">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="Название системы" />
              </template>
            </el-table-column>
            <el-table-column prop="manufacturer" label="Производитель" width="200">
              <template #default="{ row }">
                <el-input v-model="row.manufacturer" placeholder="Производитель" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Описание">
              <template #default="{ row }">
                <el-input v-model="row.description" type="textarea" :rows="2" placeholder="Описание" />
              </template>
            </el-table-column>
            <el-table-column label="Характеристики" width="300">
              <template #default="{ row }">
                <div class="flex flex-col gap-2">
                  <div
                    v-for="(feature, idx) in row.features"
                    :key="idx"
                    class="flex items-center gap-2"
                  >
                    <el-input v-model="row.features[idx]" placeholder="Характеристика" size="small" />
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeSafetyFeature(row, idx)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-button
                    type="primary"
                    size="small"
                    @click="addSafetyFeature(row)"
                  >
                    <el-icon><Plus /></el-icon>
                    Добавить характеристику
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="100" fixed="right">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeSafetySystem($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Источники газоснабжения -->
        <el-tab-pane label="Источники газоснабжения" name="gasSources">
          <div class="mb-4">
            <el-button type="primary" @click="addGasSource">
              <el-icon><Plus /></el-icon>
              Добавить источник
            </el-button>
          </div>
          <el-table :data="formData.gasSupplySources" border>
            <el-table-column prop="sourceName" label="Название источника">
              <template #default="{ row }">
                <el-input v-model="row.sourceName" placeholder="Название источника" />
              </template>
            </el-table-column>
            <el-table-column label="Действия" width="100" fixed="right">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeGasSource($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">Отмена</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">
          {{ isEdit ? 'Сохранить' : 'Создать' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import stationService from '@/services/stationService'
import { uploadFile, getPresignedDownloadUrl } from '@/services/minioService'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  station: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.station)
const formRef = ref(null)
const activeTab = ref('basic')
const saving = ref(false)
const imageFileList = ref([])
const techMapFileList = ref([])
const uploadingImage = ref(false)
const imagePreviewUrl = ref('')
const techMapPreviewUrl = ref('')
// Store photo IDs for updating existing photos
const imagePhotoId = ref(null)
const techMapPhotoId = ref(null)

// Refs for upload components and hidden inputs
const imageUploadRef = ref(null)
const techMapUploadRef = ref(null)
const imageInputRef = ref(null)
const techMapInputRef = ref(null)

function createEmptyFormData() {
  return {
    name: '',
    shortName: '',
    description: '',
    image: '',
    techMapImage: '',
    power: '',
    commissionDate: '',
    status: 'active',
    location: '',
    type: '',
    designCapacity: '',
    gasPressure: '',
    distanceFromBorder: '',
    pipelineDiameter: '',
    inputPressure: '',
    outputPressure: '',
    parallelLines: '',
    equipment: [],
    specifications: [],
    safetySystems: [],
    gasSupplySources: []
  }
}

const formData = ref(createEmptyFormData())

const rules = {
  name: [{ required: true, message: 'Введите название станции', trigger: 'blur' }],
  shortName: [{ required: true, message: 'Введите короткое название', trigger: 'blur' }],
  status: [{ required: true, message: 'Выберите статус', trigger: 'change' }]
}

// Watch for station changes to populate form
watch(() => props.station, async (newStation) => {
  if (newStation) {
    await loadStationData(newStation.id)
  } else {
    resetForm()
  }
}, { immediate: true })

// Watch for image changes to load previews
watch(() => formData.value.image, (newPath) => {
  if (newPath && !imageFileList.value.length) {
    loadImagePreview(newPath, false)
  } else {
    imagePreviewUrl.value = ''
  }
}, { immediate: true })

watch(() => formData.value.techMapImage, (newPath) => {
  if (newPath && !techMapFileList.value.length) {
    loadImagePreview(newPath, true)
  } else {
    techMapPreviewUrl.value = ''
  }
}, { immediate: true })

// Load station data for editing
async function loadStationData(stationId) {
  try {
    const data = await stationService.getStation(stationId)
    const station = data.station || data
    
    // Important: keep the same object reference for Element Plus <el-form>
    // (replacing the whole model object can prevent fields from updating).
    Object.assign(formData.value, {
      name: station.name || '',
      shortName: station.short_name || station.shortName || '',
      description: station.description || '',
      image: station.image || '',
      techMapImage: station.tech_map_image || station.techMapImage || '',
      power: station.power || '',
      commissionDate: station.commission_date || station.commissionDate || '',
      status: station.status || 'active',
      location: station.location || '',
      type: station.type || '',
      designCapacity: station.design_capacity || station.designCapacity || '',
      gasPressure: station.gas_pressure || station.gasPressure || '',
      distanceFromBorder: station.distance_from_border || station.distanceFromBorder || '',
      pipelineDiameter: station.pipeline_diameter || station.pipelineDiameter || '',
      inputPressure: station.input_pressure || station.inputPressure || '',
      outputPressure: station.output_pressure || station.outputPressure || '',
      parallelLines: station.parallel_lines || station.parallelLines || '',
    })

    // Load photos from StationPhoto
    console.log('[loadStationData] Loading photos from data:', data.photos)
    await loadStationPhotos(data.photos || [])

    // Related lists (keep array refs stable too)
    formData.value.equipment = (data.equipment || []).map(eq => ({
      id: eq.id,
      name: eq.name || '',
      model: eq.model || '',
      manufacturer: eq.manufacturer || '',
      quantity: eq.quantity || 1,
      power: eq.power || '',
      description: eq.description || ''
    }))

    formData.value.specifications = (data.specs || []).map(spec => ({
      id: spec.id,
      category: spec.category || '',
      value: spec.value || '',
      unit: spec.unit || '',
      description: spec.description || ''
    }))

    formData.value.safetySystems = (data.safety || []).map(safety => ({
      id: safety.id,
      name: safety.name || '',
      manufacturer: safety.manufacturer || '',
      description: safety.description || '',
      features: safety.features || []
    }))

    formData.value.gasSupplySources = (data.gas_sources || []).map(source => ({
      id: source.id,
      sourceName: source.source_name || source.sourceName || ''
    }))
  } catch (error) {
    ElMessage.error('Ошибка загрузки данных станции: ' + error.message)
  }
}

// Load photos from StationPhoto and display them in file lists
async function loadStationPhotos(photos) {
  console.log('[loadStationPhotos] Loading photos:', photos)
  
  // Reset photo IDs and file lists
  imagePhotoId.value = null
  techMapPhotoId.value = null
  imageFileList.value = []
  techMapFileList.value = []

  if (!photos || !Array.isArray(photos) || photos.length === 0) {
    console.log('[loadStationPhotos] No photos found')
    return
  }

  // Find photos by view type
  const stationImagePhoto = photos.find(p => p.view === 'station_image')
  const techMapPhoto = photos.find(p => p.view === 'tech_map_image')

  console.log('[loadStationPhotos] Found station_image photo:', stationImagePhoto)
  console.log('[loadStationPhotos] Found tech_map_image photo:', techMapPhoto)

  // Load station image photo
  if (stationImagePhoto && stationImagePhoto.image_url) {
    imagePhotoId.value = stationImagePhoto.id
    try {
      console.log('[loadStationPhotos] Loading presigned URL for station image:', stationImagePhoto.image_url)
      // Get presigned URL for the image
      const presignedUrl = await getPresignedDownloadUrl(
        stationImagePhoto.image_url,
        7 * 24 * 60 * 60 // 7 days
      )
      
      console.log('[loadStationPhotos] Got presigned URL for station image:', presignedUrl)
      
      // Create a file object for el-upload preview
      // el-upload requires: name, url, uid, status
      const fileName = stationImagePhoto.image_url.split('/').pop() || 'station_image.jpg'
      const fileObj = {
        name: fileName,
        url: presignedUrl,
        uid: `station-image-${stationImagePhoto.id}-${Date.now()}`,
        status: 'success',
        response: presignedUrl, // Some versions of el-upload need this
        size: 0, // Optional but may help
        percentage: 100 // Optional but may help
      }
      
      // Use nextTick to ensure reactivity
      await nextTick()
      imageFileList.value = [fileObj]
      console.log('[loadStationPhotos] Added to imageFileList:', fileObj)
      console.log('[loadStationPhotos] imageFileList.value after assignment:', imageFileList.value)
      
      // Also update formData.image for backward compatibility
      formData.value.image = stationImagePhoto.image_url
    } catch (error) {
      console.error('[loadStationPhotos] Error loading station image:', error)
      // Fallback: try to construct URL directly
      const fileName = stationImagePhoto.image_url.split('/').pop() || 'station_image.jpg'
      // Try to use MinIO service to get URL
      try {
        const { getFileUrl } = await import('@/services/minioService')
        const fallbackUrl = getFileUrl(stationImagePhoto.image_url)
        await nextTick()
        imageFileList.value = [{
          name: fileName,
          url: fallbackUrl,
          uid: `station-image-${stationImagePhoto.id}-${Date.now()}`,
          status: 'success',
          response: fallbackUrl,
          size: 0,
          percentage: 100
        }]
        console.log('[loadStationPhotos] Using fallback URL for station image:', fallbackUrl)
      } catch (fallbackError) {
        console.error('[loadStationPhotos] Fallback also failed:', fallbackError)
      }
      formData.value.image = stationImagePhoto.image_url
    }
  } else {
    console.log('[loadStationPhotos] No station_image photo found')
  }

  // Load tech map photo
  if (techMapPhoto && techMapPhoto.image_url) {
    techMapPhotoId.value = techMapPhoto.id
    try {
      console.log('[loadStationPhotos] Loading presigned URL for tech map:', techMapPhoto.image_url)
      // Get presigned URL for the image
      const presignedUrl = await getPresignedDownloadUrl(
        techMapPhoto.image_url,
        7 * 24 * 60 * 60 // 7 days
      )
      
      console.log('[loadStationPhotos] Got presigned URL for tech map:', presignedUrl)
      
      // Create a file object for el-upload preview
      const fileName = techMapPhoto.image_url.split('/').pop() || 'tech_map.jpg'
      const fileObj = {
        name: fileName,
        url: presignedUrl,
        uid: `tech-map-${techMapPhoto.id}-${Date.now()}`,
        status: 'success',
        response: presignedUrl,
        size: 0,
        percentage: 100
      }
      
      // Use nextTick to ensure reactivity
      await nextTick()
      techMapFileList.value = [fileObj]
      console.log('[loadStationPhotos] Added to techMapFileList:', fileObj)
      console.log('[loadStationPhotos] techMapFileList.value after assignment:', techMapFileList.value)
      
      // Also update formData.techMapImage for backward compatibility
      formData.value.techMapImage = techMapPhoto.image_url
    } catch (error) {
      console.error('[loadStationPhotos] Error loading tech map:', error)
      // Fallback: try to construct URL directly
      const fileName = techMapPhoto.image_url.split('/').pop() || 'tech_map.jpg'
      try {
        const { getFileUrl } = await import('@/services/minioService')
        const fallbackUrl = getFileUrl(techMapPhoto.image_url)
        await nextTick()
        techMapFileList.value = [{
          name: fileName,
          url: fallbackUrl,
          uid: `tech-map-${techMapPhoto.id}-${Date.now()}`,
          status: 'success',
          response: fallbackUrl,
          size: 0,
          percentage: 100
        }]
        console.log('[loadStationPhotos] Using fallback URL for tech map:', fallbackUrl)
      } catch (fallbackError) {
        console.error('[loadStationPhotos] Fallback also failed:', fallbackError)
      }
      formData.value.techMapImage = techMapPhoto.image_url
    }
  } else {
    console.log('[loadStationPhotos] No tech_map_image photo found')
  }
  
  // Force reactivity update
  await nextTick()
  console.log('[loadStationPhotos] Final imageFileList:', imageFileList.value)
  console.log('[loadStationPhotos] Final techMapFileList:', techMapFileList.value)
}

function resetForm() {
  Object.assign(formData.value, createEmptyFormData())
  formData.value.equipment = []
  formData.value.specifications = []
  formData.value.safetySystems = []
  formData.value.gasSupplySources = []
  imageFileList.value = []
  techMapFileList.value = []
  imagePhotoId.value = null
  techMapPhotoId.value = null
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// Equipment methods
function addEquipment() {
  formData.value.equipment.push({
    name: '',
    model: '',
    manufacturer: '',
    quantity: 1,
    power: '',
    description: ''
  })
}

function removeEquipment(index) {
  formData.value.equipment.splice(index, 1)
}

// Specification methods
function addSpecification() {
  formData.value.specifications.push({
    category: '',
    value: '',
    unit: '',
    description: ''
  })
}

function removeSpecification(index) {
  formData.value.specifications.splice(index, 1)
}

// Safety system methods
function addSafetySystem() {
  formData.value.safetySystems.push({
    name: '',
    manufacturer: '',
    description: '',
    features: []
  })
}

function removeSafetySystem(index) {
  formData.value.safetySystems.splice(index, 1)
}

function addSafetyFeature(safetySystem) {
  if (!safetySystem.features) {
    safetySystem.features = []
  }
  safetySystem.features.push('')
}

function removeSafetyFeature(safetySystem, index) {
  safetySystem.features.splice(index, 1)
}

// Gas source methods
function addGasSource() {
  formData.value.gasSupplySources.push({
    sourceName: ''
  })
}

function removeGasSource(index) {
  formData.value.gasSupplySources.splice(index, 1)
}

// Image upload handlers
async function handleImageUploadClick(event) {
  console.log('[handleImageUploadClick] Upload button clicked', event)
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  // Wait for DOM to be ready
  await nextTick()
  
  // Try to trigger file input via hidden input
  if (imageInputRef.value) {
    console.log('[handleImageUploadClick] imageInputRef found:', imageInputRef.value)
    console.log('[handleImageUploadClick] input element:', imageInputRef.value.tagName, imageInputRef.value.type)
    try {
      // Reset value to allow selecting the same file again
      imageInputRef.value.value = ''
      imageInputRef.value.click()
      console.log('[handleImageUploadClick] click() called successfully')
    } catch (error) {
      console.error('[handleImageUploadClick] Error triggering click:', error)
    }
  } else {
    console.warn('[handleImageUploadClick] imageInputRef is null, trying to find input element')
    // Fallback: try to find input element directly by ref attribute
    await nextTick()
    const inputs = document.querySelectorAll('input[type="file"][accept="image/*"]')
    console.log('[handleImageUploadClick] Found inputs via querySelector:', inputs.length)
    if (inputs.length > 0) {
      console.log('[handleImageUploadClick] Using first input, triggering click')
      inputs[0].value = '' // Reset value
      inputs[0].click()
    } else {
      console.error('[handleImageUploadClick] Could not find input element')
    }
  }
}

async function handleTechMapUploadClick(event) {
  console.log('[handleTechMapUploadClick] Upload button clicked', event)
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  // Wait for DOM to be ready
  await nextTick()
  
  // Try to trigger file input via hidden input
  if (techMapInputRef.value) {
    console.log('[handleTechMapUploadClick] techMapInputRef found:', techMapInputRef.value)
    console.log('[handleTechMapUploadClick] input element:', techMapInputRef.value.tagName, techMapInputRef.value.type)
    try {
      // Reset value to allow selecting the same file again
      techMapInputRef.value.value = ''
      techMapInputRef.value.click()
      console.log('[handleTechMapUploadClick] click() called successfully')
    } catch (error) {
      console.error('[handleTechMapUploadClick] Error triggering click:', error)
    }
  } else {
    console.warn('[handleTechMapUploadClick] techMapInputRef is null, trying to find input element')
    // Fallback: try to find input element directly
    await nextTick()
    const inputs = document.querySelectorAll('input[type="file"][accept="image/*"]')
    console.log('[handleTechMapUploadClick] Found inputs via querySelector:', inputs.length)
    if (inputs.length > 1) {
      console.log('[handleTechMapUploadClick] Using second input, triggering click')
      inputs[1].value = '' // Reset value
      inputs[1].click() // Second input is for tech map
    } else if (inputs.length === 1) {
      console.log('[handleTechMapUploadClick] Using only input found, triggering click')
      inputs[0].value = '' // Reset value
      inputs[0].click()
    } else {
      console.error('[handleTechMapUploadClick] Could not find input element')
    }
  }
}

function handleImageInputChange(event) {
  console.log('[handleImageInputChange] File input changed:', event)
  const file = event.target.files?.[0]
  if (file) {
    console.log('[handleImageInputChange] File selected:', file.name, file.type, file.size)
    // Create a file object compatible with el-upload
    const uploadFile = {
      name: file.name,
      size: file.size,
      type: file.type,
      raw: file,
      uid: Date.now()
    }
    handleImageChange(uploadFile, [uploadFile])
  } else {
    console.warn('[handleImageInputChange] No file selected')
  }
}

function handleTechMapInputChange(event) {
  console.log('[handleTechMapInputChange] File input changed:', event)
  const file = event.target.files?.[0]
  if (file) {
    console.log('[handleTechMapInputChange] File selected:', file.name, file.type, file.size)
    // Create a file object compatible with el-upload
    const uploadFile = {
      name: file.name,
      size: file.size,
      type: file.type,
      raw: file,
      uid: Date.now()
    }
    handleTechMapChange(uploadFile, [uploadFile])
  } else {
    console.warn('[handleTechMapInputChange] No file selected')
  }
}

function handleImageChange(file, fileList) {
  console.log('[handleImageChange] File selected:', file?.name, 'FileList length:', fileList?.length)
  imageFileList.value = fileList
  if (file && file.raw) {
    // Show preview immediately
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreviewUrl.value = e.target.result
      console.log('[handleImageChange] Preview URL created')
    }
    reader.onerror = (e) => {
      console.error('[handleImageChange] Error reading file:', e)
    }
    reader.readAsDataURL(file.raw)
  } else {
    console.warn('[handleImageChange] No file.raw found')
  }
}

function handleTechMapChange(file, fileList) {
  console.log('[handleTechMapChange] File selected:', file?.name, 'FileList length:', fileList?.length)
  techMapFileList.value = fileList
  if (file && file.raw) {
    // Show preview immediately
    const reader = new FileReader()
    reader.onload = (e) => {
      techMapPreviewUrl.value = e.target.result
      console.log('[handleTechMapChange] Preview URL created')
    }
    reader.onerror = (e) => {
      console.error('[handleTechMapChange] Error reading file:', e)
    }
    reader.readAsDataURL(file.raw)
  } else {
    console.warn('[handleTechMapChange] No file.raw found')
  }
}

// Helper functions for image URLs
function isImageUrl(path) {
  if (!path) return false
  return path.startsWith('http') || path.startsWith('/') || path.includes('.jpg') || path.includes('.png') || path.includes('.jpeg') || path.includes('stations/') || path.includes('tex_kart/')
}

async function loadImagePreview(path, isTechMap = false) {
  if (!path || !isImageUrl(path)) {
    if (isTechMap) {
      techMapPreviewUrl.value = ''
    } else {
      imagePreviewUrl.value = ''
    }
    return
  }

  try {
    let url = path
    // If it's already a full URL, use it
    if (path.startsWith('http')) {
      url = path
    } else if (path.startsWith('stations/') || path.startsWith('tex_kart/') || path.includes('/')) {
      // MinIO path - get presigned URL
      const { getPresignedDownloadUrl } = await import('@/services/minioService')
      url = await getPresignedDownloadUrl(path, 7 * 24 * 60 * 60)
    } else if (path && !path.includes('/')) {
      // Old format: just filename, assume it's in stations folder
      const { getPresignedDownloadUrl } = await import('@/services/minioService')
      url = await getPresignedDownloadUrl(`stations/${path}`, 7 * 24 * 60 * 60)
    }

    if (isTechMap) {
      techMapPreviewUrl.value = url
    } else {
      imagePreviewUrl.value = url
    }
  } catch (error) {
    console.error('Error loading image preview:', error)
    // Fallback to public path
    if (isTechMap) {
      techMapPreviewUrl.value = path.startsWith('/') ? path : `/tex_kart/${path}`
    } else {
      imagePreviewUrl.value = path.startsWith('/') ? path : `/stations/${path}`
    }
  }
}

function handleImageError(event) {
  // Hide broken image
  event.target.style.display = 'none'
}

// Upload images to MinIO
async function uploadImages() {
  // Upload station image - only if there's a new file (has .raw property)
  if (imageFileList.value.length > 0) {
    const fileItem = imageFileList.value[0]
    const file = fileItem.raw
    // Only upload if it's a new file (has raw property), not an existing one loaded from StationPhoto
    if (file) {
      console.log('[uploadImages] Uploading new station image file:', file.name)
      uploadingImage.value = true
      try {
        const result = await uploadFile(file, 'stations')
        // Save object name (path in MinIO) to formData
        formData.value.image = result.objectName
        console.log('[uploadImages] Station image uploaded, objectName:', result.objectName)
        ElMessage.success('Изображение станции загружено')
      } catch (error) {
        ElMessage.error('Ошибка загрузки изображения: ' + error.message)
        throw error
      } finally {
        uploadingImage.value = false
      }
    } else {
      console.log('[uploadImages] Station image already exists, using existing URL:', fileItem.url)
      // If file doesn't have .raw, it's an existing file from StationPhoto
      // Make sure formData.image is set to the image_url from StationPhoto
      if (fileItem.url && !formData.value.image) {
        // Try to extract object key from URL or use the existing path
        // This should already be set in loadStationPhotos, but just in case
        console.log('[uploadImages] Using existing station image URL')
      }
    }
  }

  // Upload tech map image - only if there's a new file (has .raw property)
  if (techMapFileList.value.length > 0) {
    const fileItem = techMapFileList.value[0]
    const file = fileItem.raw
    // Only upload if it's a new file (has raw property), not an existing one loaded from StationPhoto
    if (file) {
      console.log('[uploadImages] Uploading new tech map file:', file.name)
      uploadingImage.value = true
      try {
        const result = await uploadFile(file, 'tex_kart')
        // Save object name (path in MinIO) to formData
        formData.value.techMapImage = result.objectName
        console.log('[uploadImages] Tech map uploaded, objectName:', result.objectName)
        ElMessage.success('Техническая карта загружена')
      } catch (error) {
        ElMessage.error('Ошибка загрузки технической карты: ' + error.message)
        throw error
      } finally {
        uploadingImage.value = false
      }
    } else {
      console.log('[uploadImages] Tech map already exists, using existing URL:', fileItem.url)
      // If file doesn't have .raw, it's an existing file from StationPhoto
      // Make sure formData.techMapImage is set to the image_url from StationPhoto
      if (fileItem.url && !formData.value.techMapImage) {
        console.log('[uploadImages] Using existing tech map URL')
      }
    }
  }
}

// Save photos to StationPhoto after station is saved
async function saveStationPhotos(stationId) {
  // Save station image photo
  if (formData.value.image) {
    try {
      await stationService.createOrUpdateStationPhoto(stationId, {
        view: 'station_image',
        imageUrl: formData.value.image,
        title: 'Фото станции'
      })
    } catch (error) {
      console.error('[saveStationPhotos] Error saving station image:', error)
      // Don't throw - backend will also try to sync photos
    }
  }

  // Save tech map photo
  if (formData.value.techMapImage) {
    try {
      await stationService.createOrUpdateStationPhoto(stationId, {
        view: 'tech_map_image',
        imageUrl: formData.value.techMapImage,
        title: 'Техническая карта'
      })
    } catch (error) {
      console.error('[saveStationPhotos] Error saving tech map:', error)
      // Don't throw - backend will also try to sync photos
    }
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    // Upload images first if there are new files
    await uploadImages()

    // Save main station data
    let station
    let stationId
    
    if (isEdit.value) {
      station = await stationService.updateStation(props.station.id, formData.value)
      stationId = station.id || props.station.id
    } else {
      station = await stationService.createStation(formData.value)
      // For new station, ensure we have the ID
      if (!station.id) {
        // If ID is not returned, try to get it from the response
        // or reload the station list to get the latest ID
        ElMessage.warning('Станция создана, но не удалось получить ID. Пожалуйста, обновите список станций.')
        emit('saved')
        handleClose()
        return
      }
      stationId = station.id
    }

    // Save photos to StationPhoto (backend also does this automatically, but we do it explicitly for reliability)
    if (stationId) {
      await saveStationPhotos(stationId)
    }

    // Save related data
    if (stationId) {
      try {
        let existingEquipment = []
        let existingSpecs = []
        let existingSafety = []
        let existingGasSources = []

        // Get existing data only for edit mode
        if (isEdit.value) {
          const existingData = await stationService.getStation(stationId)
          existingEquipment = existingData.equipment || []
          existingSpecs = existingData.specs || []
          existingSafety = existingData.safety || []
          existingGasSources = existingData.gas_sources || []
        }

        // Save equipment
        if (isEdit.value) {
          // Delete removed equipment
          const equipmentIds = formData.value.equipment.map(eq => eq.id).filter(Boolean)
          for (const eq of existingEquipment) {
            if (!equipmentIds.includes(eq.id)) {
              await stationService.deleteEquipment(stationId, eq.id)
            }
          }
        }
        // Create/update equipment
        for (const eq of formData.value.equipment) {
          if (eq.id && isEdit.value) {
            await stationService.updateEquipment(stationId, eq.id, eq)
          } else {
            await stationService.createEquipment(stationId, eq)
          }
        }

        // Save specifications
        if (isEdit.value) {
          // Delete removed specs
          const specIds = formData.value.specifications.map(spec => spec.id).filter(Boolean)
          for (const spec of existingSpecs) {
            if (!specIds.includes(spec.id)) {
              await stationService.deleteSpecification(stationId, spec.id)
            }
          }
        }
        // Create/update specifications
        for (const spec of formData.value.specifications) {
          if (spec.id && isEdit.value) {
            await stationService.updateSpecification(stationId, spec.id, spec)
          } else {
            await stationService.createSpecification(stationId, spec)
          }
        }

        // Save safety systems
        if (isEdit.value) {
          // Delete removed safety systems
          const safetyIds = formData.value.safetySystems.map(s => s.id).filter(Boolean)
          for (const safety of existingSafety) {
            if (!safetyIds.includes(safety.id)) {
              await stationService.deleteSafetySystem(stationId, safety.id)
            }
          }
        }
        // Create/update safety systems
        for (const safety of formData.value.safetySystems) {
          let safetyId = safety.id
          if (!safetyId || !isEdit.value) {
            const created = await stationService.createSafetySystem(stationId, safety)
            safetyId = created.id
          } else {
            await stationService.updateSafetySystem(stationId, safetyId, safety)
          }

          // Save features - only create new ones (for simplicity)
          // In production, you might want to track and delete removed features
          if (safety.features && safety.features.length > 0) {
            for (const feature of safety.features) {
              if (typeof feature === 'string' && feature.trim()) {
                await stationService.createSafetySystemFeature(stationId, safetyId, {
                  featureName: feature
                })
              }
            }
          }
        }

        // Save gas sources
        if (isEdit.value) {
          // Delete removed gas sources
          const sourceIds = formData.value.gasSupplySources.map(s => s.id).filter(Boolean)
          for (const source of existingGasSources) {
            if (!sourceIds.includes(source.id)) {
              await stationService.deleteGasSupplySource(stationId, source.id)
            }
          }
        }
        // Create/update gas sources
        for (const source of formData.value.gasSupplySources) {
          if (source.id && isEdit.value) {
            await stationService.updateGasSupplySource(stationId, source.id, source)
          } else if (source.sourceName && source.sourceName.trim()) {
            await stationService.createGasSupplySource(stationId, source)
          }
        }
      } catch (error) {
        console.error('Error saving related data:', error)
        // Don't fail the whole operation if related data fails
        ElMessage.warning('Станция сохранена, но возникли проблемы с сохранением связанных данных: ' + error.message)
      }
    }

    ElMessage.success(isEdit.value ? 'Станция обновлена' : 'Станция создана')
    emit('saved')
    handleClose()
  } catch (error) {
    ElMessage.error('Ошибка сохранения: ' + error.message)
  } finally {
    saving.value = false
  }
}

function handleClose() {
  visible.value = false
  resetForm()
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.upload-wrapper {
  position: relative;
  display: inline-block;
}

.upload-label {
  display: block;
  cursor: pointer;
  position: relative;
}

.upload-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.upload-button {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 148px;
  height: 148px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.upload-button:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.upload-image {
  width: 100%;
}

.upload-image :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer !important;
  position: relative;
  overflow: visible;
  transition: all 0.3s;
  width: 148px;
  height: 148px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1;
  pointer-events: auto !important;
}

.upload-image :deep(.el-upload:hover) {
  border-color: #409eff;
}

.upload-image :deep(.el-upload--picture-card) {
  cursor: pointer !important;
  pointer-events: auto !important;
}

.upload-image :deep(.el-upload--picture-card *) {
  pointer-events: none;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 12px;
  color: #8c939d;
  text-align: center;
}
</style>

