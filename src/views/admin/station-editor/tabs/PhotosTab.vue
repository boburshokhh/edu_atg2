<template>
  <div>
    <div class="mb-4">
      <input
        ref="photoInput"
        type="file"
        class="hidden"
        accept="image/*"
        @change="handlePhotoUpload"
      >
      <el-button
        type="primary"
        :loading="uploadingPhoto"
        @click="$refs.photoInput.click()"
      >
        <el-icon class="mr-2">
          <Upload />
        </el-icon> Загрузить фото
      </el-button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <el-card
        v-for="photo in photos"
        :key="photo.id"
        :body-style="{ padding: '0px' }"
      >
        <img
          :src="photo.displayUrl || photo.image_url"
          class="w-full h-48 object-cover cursor-pointer hover:opacity-90 transition-opacity"
          @click="openPhotoLightbox(photo)"
        >
        <div class="p-4">
          <div class="mb-2">
            <el-input
              v-model="photo.title"
              placeholder="Название"
              size="small"
              @change="updatePhoto(photo)"
            />
          </div>
          <div class="mb-2">
            <el-select
              v-model="photo.view"
              placeholder="Вид"
              size="small"
              style="width: 100%"
              @change="updatePhoto(photo)"
            >
              <el-option
                label="Общий вид"
                value="general"
              />
              <el-option
                label="Машинный зал"
                value="machine-hall"
              />
              <el-option
                label="Компрессоры"
                value="compressors"
              />
              <el-option
                label="Охлаждение"
                value="cooling"
              />
              <el-option
                label="Другое"
                value="other"
              />
            </el-select>
          </div>
          <div class="flex justify-between items-center mt-2">
            <el-button
              type="danger"
              link
              size="small"
              @click="deletePhoto(photo)"
            >
              Удалить
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Lightbox для просмотра фотографий -->
    <vue-easy-lightbox
      :visible="lightboxVisible"
      :imgs="lightboxImages"
      :index="lightboxIndex"
      @hide="lightboxVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import { Upload } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'

const {
  photos,
  uploadingPhoto,
  handlePhotoUpload,
  updatePhoto,
  deletePhoto
} = useStationEditorContext()

// Lightbox для фотографий
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)
const lightboxImages = computed(() => {
  return photos.value.map(photo => photo.displayUrl || photo.image_url)
})

const openPhotoLightbox = (photo) => {
  const index = photos.value.findIndex(p => 
    (p.displayUrl || p.image_url) === (photo.displayUrl || photo.image_url)
  )
  lightboxIndex.value = index >= 0 ? index : 0
  lightboxVisible.value = true
}
</script>

