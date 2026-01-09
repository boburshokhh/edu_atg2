import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import stationService from '@/services/stationService'
import { deleteFile } from '@/services/minioService'

export function useDocsCrud(station, docs, loadData) {
  const uploadingDoc = ref(false)

  const handleDocUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    uploadingDoc.value = true
    try {
      const key = await stationService.uploadFile(file, `stations/${station.value.id}/docs`)
      await stationService.createNormativeDoc(station.value.id, {
        title: file.name,
        file_url: key
      })
      ElMessage.success('Документ загружен')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка загрузки документа: ' + error.message)
    } finally {
      uploadingDoc.value = false
      event.target.value = ''
    }
  }

  const deleteDoc = async (doc) => {
    try {
      await ElMessageBox.confirm(
        'Вы уверены, что хотите удалить этот документ? Файл будет удален из хранилища.',
        'Подтверждение удаления',
        {
          confirmButtonText: 'Удалить',
          cancelButtonText: 'Отмена',
          type: 'warning'
        }
      )

      const fileUrl = doc.file_url
      
      // Удаляем запись из БД
      await stationService.deleteNormativeDoc(station.value.id, doc.id)
      
      // Удаляем файл из MinIO, если есть file_url
      if (fileUrl && !fileUrl.startsWith('http')) {
        try {
          await deleteFile(fileUrl)
        } catch (fileError) {
          console.warn('Не удалось удалить файл из MinIO:', fileError)
          // Продолжаем, даже если удаление файла не удалось
        }
      }
      
      ElMessage.success('Документ удален')
      docs.value = docs.value.filter(d => d.id !== doc.id)
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('Ошибка удаления: ' + error.message)
      }
    }
  }

  return {
    uploadingDoc,
    handleDocUpload,
    deleteDoc
  }
}

