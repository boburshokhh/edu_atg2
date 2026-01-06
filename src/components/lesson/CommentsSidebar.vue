<template>
  <SidebarShell
    :is-open="isOpen"
    @close="handleClose"
  >
    <template #header>Комментарии</template>

    <!-- Comments List -->
    <div class="p-5 flex flex-col gap-6">
      <div v-if="isLoading" class="flex items-center justify-center py-8">
        <el-icon class="is-loading text-2xl text-slate-400">
          <Loading />
        </el-icon>
      </div>

      <div v-else-if="error" class="text-center py-8">
        <p class="text-sm text-red-500">{{ error }}</p>
        <el-button
          type="primary"
          size="small"
          class="mt-2"
          @click="loadComments"
        >
          Повторить
        </el-button>
      </div>

      <template v-else-if="comments.length > 0">
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="flex gap-3"
        >
          <div
            :class="[
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold',
              getAvatarColor(comment.userRole, comment.userName)
            ]"
          >
            {{ getUserInitials(comment.userName) }}
          </div>
          <div class="flex flex-col gap-1.5 flex-1">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-slate-800">{{ comment.userName }}</span>
                <span
                  v-if="comment.userRole === 'admin' || comment.userRole === 'instructor'"
                  class="px-1.5 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wide"
                >
                  {{ comment.userRole === 'admin' ? 'Админ' : 'Инструктор' }}
                </span>
              </div>
              <span class="text-[10px] text-slate-400">{{ formatTimeAgo(comment.createdAt) }}</span>
            </div>
            <p class="text-sm text-slate-600 leading-relaxed">{{ comment.text }}</p>
          </div>
        </div>
      </template>

      <!-- Улучшенный empty state с иллюстрацией и призывом к действию -->
      <div v-else class="text-center py-12 px-4">
        <div class="flex flex-col items-center gap-4">
          <div class="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center">
            <span class="material-symbols-outlined text-4xl text-slate-400">chat_bubble_outline</span>
          </div>
          <div class="flex flex-col gap-2">
            <p class="text-base font-semibold text-slate-700">Пока нет комментариев</p>
            <p class="text-sm text-[#757575] max-w-xs">
              Станьте первым, кто оставит комментарий! Ваши вопросы и обсуждения помогают всем лучше понять материал.
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <!-- Comment Form с улучшенным padding и группировкой элементов -->
      <div class="p-4 bg-slate-50 border-t border-slate-200">
      <form @submit.prevent="handleSubmit" class="flex flex-col gap-3">
        <!-- Textarea с увеличенным padding и min-height -->
        <el-input
          v-model="newCommentText"
          type="textarea"
          :rows="4"
          placeholder="Введите ваш комментарий..."
          :disabled="isSubmitting"
          class="custom-scrollbar comment-textarea"
          :style="{ minHeight: '100px' }"
        />
        <!-- Визуально сгруппированная toolbar -->
        <div class="flex justify-between items-center pt-2 border-t border-slate-200">
          <!-- Группа кнопок управления (emoji, attachment) -->
          <div class="flex gap-2 items-center">
            <button
              type="button"
              class="p-2 hover:bg-slate-200 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              title="Эмодзи"
              tabindex="0"
            >
              <span class="material-symbols-outlined text-[20px] text-slate-600">sentiment_satisfied</span>
            </button>
            <button
              type="button"
              class="p-2 hover:bg-slate-200 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              title="Прикрепить файл"
              tabindex="0"
            >
              <span class="material-symbols-outlined text-[20px] text-slate-600">attach_file</span>
            </button>
          </div>
          <!-- Кнопка отправки отделена визуально -->
          <el-button
            type="primary"
            :loading="isSubmitting"
            :disabled="!newCommentText.trim()"
            native-type="submit"
            class="flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
            tabindex="0"
          >
            Отправить
            <el-icon>
              <Promotion />
            </el-icon>
          </el-button>
        </div>
      </form>
      </div>
    </template>
  </SidebarShell>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Promotion } from '@element-plus/icons-vue'
import SidebarShell from '@/components/ui/SidebarShell.vue'
import commentsService from '@/services/commentsService'
import authService from '@/services/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  stationId: {
    type: Number,
    required: true
  },
  lessonIndex: {
    type: Number,
    default: null
  },
  topicIndex: {
    type: Number,
    default: null
  },
  fileObjectKey: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close'])

const comments = ref([])
const isLoading = ref(false)
const error = ref(null)
const newCommentText = ref('')
const isSubmitting = ref(false)

// Get user initials for avatar
const getUserInitials = (name) => {
  if (!name) return 'U'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.charAt(0).toUpperCase()
}

// Get avatar color based on user role or name
const getAvatarColor = (role, name) => {
  const colors = [
    'bg-teal-100 text-teal-600',
    'bg-blue-100 text-blue-600',
    'bg-purple-100 text-purple-600',
    'bg-pink-100 text-pink-600',
    'bg-orange-100 text-orange-600'
  ]
  
  if (role === 'admin' || role === 'instructor') {
    return 'bg-primary/10 text-primary'
  }
  
  // Use name hash for consistent color
  const hash = name ? name.charCodeAt(0) : 0
  return colors[hash % colors.length]
}

// Format time ago
const formatTimeAgo = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'только что'
  if (diffMins < 60) return `${diffMins} мин назад`
  if (diffHours < 24) return `${diffHours} ч назад`
  if (diffDays < 7) return `${diffDays} дн назад`
  
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

const loadComments = async () => {
  if (!props.stationId) return

  isLoading.value = true
  error.value = null

  try {
    const data = await commentsService.getComments({
      stationId: props.stationId,
      lessonIndex: props.lessonIndex,
      topicIndex: props.topicIndex,
      fileObjectKey: props.fileObjectKey
    })
    comments.value = data || []
  } catch (err) {
    console.error('[CommentsSidebar] Error loading comments:', err)
    error.value = err.message || 'Не удалось загрузить комментарии'
    ElMessage.error('Не удалось загрузить комментарии')
  } finally {
    isLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!newCommentText.value.trim() || isSubmitting.value) return

  isSubmitting.value = true

  try {
    const newComment = await commentsService.createComment({
      stationId: props.stationId,
      lessonIndex: props.lessonIndex,
      topicIndex: props.topicIndex,
      fileObjectKey: props.fileObjectKey,
      commentText: newCommentText.value.trim()
    })

    // Add new comment to the beginning of the list
    comments.value.unshift(newComment)
    newCommentText.value = ''
    ElMessage.success('Комментарий добавлен')
  } catch (err) {
    console.error('[CommentsSidebar] Error creating comment:', err)
    ElMessage.error('Не удалось отправить комментарий')
  } finally {
    isSubmitting.value = false
  }
}

const handleClose = () => {
  emit('close')
}

// Watch for changes in lesson/topic/file to reload comments
watch(
  () => [props.stationId, props.lessonIndex, props.topicIndex, props.fileObjectKey],
  () => {
    if (props.isOpen && props.stationId) {
      loadComments()
    }
  },
  { immediate: false }
)

// Load comments when sidebar opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.stationId) {
    loadComments()
  }
})

onMounted(() => {
  if (props.isOpen && props.stationId) {
    loadComments()
  }
})
</script>


<style scoped>
/* Увеличенный padding для textarea комментариев */
:deep(.comment-textarea .el-textarea__inner) {
  padding: 12px 16px !important;
  min-height: 100px !important;
  font-size: 14px;
  line-height: 1.5;
  border-radius: 8px;
  transition: border-color 0.2s;
}

:deep(.comment-textarea .el-textarea__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>

