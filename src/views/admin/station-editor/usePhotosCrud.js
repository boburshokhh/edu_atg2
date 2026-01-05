import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function usePhotosCrud(station, photos, loadData) {
  const uploadingPhoto = ref(false)

  const handlePhotoUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    uploadingPhoto.value = true
    try {
      const key = await stationService.uploadFile(file, `stations/${station.value.id}/photos`)
      await stationService.createPhoto(station.value.id, {
        title: file.name,
        view: 'other',
        image_url: key
      })
      ElMessage.success('Фото загружено')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка загрузки фото: ' + error.message)
    } finally {
      uploadingPhoto.value = false
      event.target.value = ''
    }
  }

  const updatePhoto = async (photo) => {
    try {
      await stationService.updatePhoto(station.value.id, photo.id, photo)
      ElMessage.success('Фото обновлено')
    } catch (error) {
      ElMessage.error('Ошибка обновления: ' + error.message)
    }
  }

  const deletePhoto = async (photo) => {
    try {
      await stationService.deletePhoto(station.value.id, photo.id)
      ElMessage.success('Фото удалено')
      photos.value = photos.value.filter(p => p.id !== photo.id)
    } catch (error) {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }

  return {
    uploadingPhoto,
    handlePhotoUpload,
    updatePhoto,
    deletePhoto
  }
}

