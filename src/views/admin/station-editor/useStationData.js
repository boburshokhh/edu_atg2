import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useStationData() {
  const route = useRoute()
  const loading = ref(false)
  const station = ref({
    name: '',
    short_name: '',
    status: 'active',
    courses_count: 0
  })
  const photos = ref([])
  const docs = ref([])
  const equipment = ref([])
  const specs = ref([])
  const safetySystems = ref([])
  const gasSources = ref([])

  const isEditing = computed(() => route.params.id !== 'new')

  const loadData = async () => {
    if (!isEditing.value) return
    
    loading.value = true
    try {
      const data = await stationService.getStation(route.params.id)
      station.value = { ...data.station }
      photos.value = data.photos || []
      docs.value = data.normativeDocs || []
      equipment.value = data.equipment || []
      specs.value = data.specs || []
      safetySystems.value = (data.safety || []).map(s => ({
        ...s,
        features: Array.isArray(s.features) ? s.features : [],
        feature_names: s.feature_names || (Array.isArray(s.features) ? s.features.map(f => typeof f === 'string' ? f : f.feature_name) : [])
      }))
      gasSources.value = data.gas_sources || []
      
      // Convert Minio keys to URLs for photos
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
      for (const photo of photos.value) {
        if (photo.image_url && !photo.image_url.startsWith('http')) {
          photo.displayUrl = `${API_BASE_URL}/files/stream/${encodeURIComponent(photo.image_url)}`
        } else {
          photo.displayUrl = photo.image_url
        }
      }
      
      // Convert Minio keys to URLs for docs
      for (const doc of docs.value) {
        if (doc.file_url && !doc.file_url.startsWith('http')) {
          doc.downloadUrl = `${API_BASE_URL}/files/stream/${encodeURIComponent(doc.file_url)}`
        } else {
          doc.downloadUrl = doc.file_url
        }
      }
    } catch (error) {
      ElMessage.error('Ошибка загрузки данных: ' + error.message)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    station,
    photos,
    docs,
    equipment,
    specs,
    safetySystems,
    gasSources,
    isEditing,
    loadData
  }
}

