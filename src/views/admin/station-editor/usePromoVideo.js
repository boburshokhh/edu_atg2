import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'
import minioService from '@/services/minioService'

export function usePromoVideo(station, isEditing) {
  const route = useRoute()
  const promoVideo = ref(null)
  const promoVideoUrl = ref('')
  const uploadingPromoVideo = ref(false)

  const loadPromoVideo = async () => {
    if (!isEditing.value) return
    promoVideoUrl.value = ''
    try {
      promoVideo.value = await stationService.getStationPromoVideo(route.params.id)
      if (promoVideo.value?.objectKey) {
        promoVideoUrl.value = await minioService.getPresignedDownloadUrl(
          promoVideo.value.objectKey,
          7 * 24 * 60 * 60,
          'video/mp4'
        )
      }
    } catch (e) {
      console.error('[StationEditor] Failed to load promo video:', e)
      promoVideo.value = null
      promoVideoUrl.value = ''
    }
  }

  const handlePromoVideoUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    uploadingPromoVideo.value = true
    try {
      const key = await stationService.uploadFile(file, `stations/${station.value.id}/promo_video`)
      const payload = {
        title: file.name,
        objectKey: key
      }
      const resp = await stationService.updateStationPromoVideo(route.params.id, payload)
      promoVideo.value = resp?.video || null
      promoVideoUrl.value = await minioService.getPresignedDownloadUrl(key, 7 * 24 * 60 * 60, file.type || 'video/mp4')
      ElMessage.success('Видео загружено')
    } catch (e) {
      ElMessage.error('Ошибка загрузки видео: ' + (e?.message || e))
    } finally {
      uploadingPromoVideo.value = false
      event.target.value = ''
    }
  }

  const deletePromoVideo = async ({ deleteObject = false } = {}) => {
    try {
      await stationService.deleteStationPromoVideo(route.params.id, { deleteObject })
      promoVideo.value = null
      promoVideoUrl.value = ''
      ElMessage.success('Видео удалено')
    } catch (e) {
      ElMessage.error('Ошибка удаления видео: ' + (e?.message || e))
    }
  }

  return {
    promoVideo,
    promoVideoUrl,
    uploadingPromoVideo,
    loadPromoVideo,
    handlePromoVideoUpload,
    deletePromoVideo
  }
}

