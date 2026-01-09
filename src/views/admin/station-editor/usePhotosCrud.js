import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import stationService from '@/services/stationService'
import { deleteFile } from '@/services/minioService'

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
      await ElMessageBox.confirm(
        'Вы уверены, что хотите удалить это фото? Файл будет удален из хранилища.',
        'Подтверждение удаления',
        {
          confirmButtonText: 'Удалить',
          cancelButtonText: 'Отмена',
          type: 'warning'
        }
      )

      const imageUrl = photo.image_url
      
      // Удаляем запись из БД
      await stationService.deletePhoto(station.value.id, photo.id)
      
      // Удаляем файл из MinIO, если есть image_url
      if (imageUrl && !imageUrl.startsWith('http')) {
        try {
          await deleteFile(imageUrl)
        } catch (fileError) {
          console.warn('Не удалось удалить файл из MinIO:', fileError)
          // Продолжаем, даже если удаление файла не удалось
        }
      }
      
      ElMessage.success('Фото удалено')
      photos.value = photos.value.filter(p => p.id !== photo.id)
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('Ошибка удаления: ' + error.message)
      }
    }
  }

  return {
    uploadingPhoto,
    handlePhotoUpload,
    updatePhoto,
    deletePhoto
  }
}

