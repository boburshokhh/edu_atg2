<template>
  <div class="comments-section p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-bold text-gray-900">
        Комментарии
        <el-tag class="ml-2" size="small">{{ comments.length }}</el-tag>
      </h3>
      <el-button 
        type="primary" 
        size="small" 
        @click="showCommentForm = !showCommentForm"
        :icon="showCommentForm ? Close : Edit"
      >
        {{ showCommentForm ? 'Отмена' : 'Добавить комментарий' }}
      </el-button>
    </div>

    <!-- Add Comment Form -->
    <el-collapse-transition>
      <div v-show="showCommentForm" class="mb-6">
        <el-card shadow="never" class="comment-form-card">
          <el-form @submit.prevent="submitComment">
            <el-form-item>
              <el-input
                v-model="newComment"
                type="textarea"
                :rows="4"
                placeholder="Поделитесь своими мыслями о материале..."
                maxlength="1000"
                show-word-limit
              />
            </el-form-item>
            <el-form-item class="mb-0">
              <div class="flex justify-end gap-2">
                <el-button @click="showCommentForm = false">Отмена</el-button>
                <el-button 
                  type="primary" 
                  @click="submitComment"
                  :disabled="!newComment.trim()"
                >
                  Отправить комментарий
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </el-collapse-transition>

    <!-- Comments List -->
    <div v-if="comments.length > 0" class="space-y-4">
      <el-card 
        v-for="comment in sortedComments" 
        :key="comment.id"
        shadow="hover"
        class="comment-card"
      >
        <!-- Comment Header -->
        <div class="flex items-start gap-3 mb-3">
          <el-avatar 
            :size="40" 
            :src="comment.authorAvatar"
            class="flex-shrink-0"
          >
            <el-icon :size="20"><User /></el-icon>
          </el-avatar>
          
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-semibold text-gray-900">{{ comment.author }}</span>
              <el-tag v-if="comment.isInstructor" type="warning" size="small">Преподаватель</el-tag>
              <el-tag v-if="comment.isAuthor" type="success" size="small">Вы</el-tag>
            </div>
            <div class="text-xs text-gray-500">
              {{ formatTimestamp(comment.timestamp) }}
            </div>
          </div>

          <!-- Actions Menu -->
          <el-dropdown trigger="click" @command="handleCommentAction">
            <el-button :icon="MoreFilled" circle size="small" text />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item 
                  :command="{ action: 'edit', commentId: comment.id }"
                  v-if="comment.isAuthor"
                >
                  <el-icon><Edit /></el-icon>
                  Редактировать
                </el-dropdown-item>
                <el-dropdown-item 
                  :command="{ action: 'delete', commentId: comment.id }"
                  v-if="comment.isAuthor"
                >
                  <el-icon><Delete /></el-icon>
                  Удалить
                </el-dropdown-item>
                <el-dropdown-item 
                  :command="{ action: 'report', commentId: comment.id }"
                  v-if="!comment.isAuthor"
                >
                  <el-icon><Warning /></el-icon>
                  Пожаловаться
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- Comment Content -->
        <div class="mb-3">
          <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{{ comment.content }}</p>
        </div>

        <!-- Comment Actions -->
        <div class="flex items-center gap-4 text-sm">
          <el-button 
            text 
            size="small"
            @click="likeComment(comment.id)"
            :class="comment.isLiked ? 'text-blue-600' : 'text-gray-500'"
          >
            <el-icon class="mr-1"><Star :class="comment.isLiked ? 'fill-blue-600' : ''" /></el-icon>
            {{ comment.likes || 0 }}
          </el-button>
          
          <el-button 
            text 
            size="small"
            @click="toggleReplyForm(comment.id)"
            class="text-gray-500"
          >
            <el-icon class="mr-1"><ChatDotRound /></el-icon>
            Ответить
          </el-button>

          <el-button 
            text 
            size="small"
            v-if="comment.replies?.length > 0"
            @click="toggleReplies(comment.id)"
          >
            {{ showReplies[comment.id] ? 'Скрыть' : 'Показать' }} 
            {{ comment.replies.length }} 
            {{ comment.replies.length === 1 ? 'ответ' : 'ответов' }}
          </el-button>
        </div>

        <!-- Reply Form -->
        <el-collapse-transition>
          <div v-show="replyFormVisible[comment.id]" class="mt-4 pl-12">
            <el-input
              v-model="replyTexts[comment.id]"
              type="textarea"
              :rows="3"
              placeholder="Написать ответ..."
              maxlength="500"
              show-word-limit
            />
            <div class="flex justify-end gap-2 mt-2">
              <el-button size="small" @click="toggleReplyForm(comment.id)">
                Отмена
              </el-button>
              <el-button 
                type="primary" 
                size="small"
                @click="submitReply(comment.id)"
                :disabled="!replyTexts[comment.id]?.trim()"
              >
                Ответить
              </el-button>
            </div>
          </div>
        </el-collapse-transition>

        <!-- Replies -->
        <el-collapse-transition>
          <div v-show="showReplies[comment.id] && comment.replies?.length > 0" class="mt-4 space-y-3">
            <div 
              v-for="reply in comment.replies" 
              :key="reply.id"
              class="flex items-start gap-3 pl-12 pt-3 border-t border-gray-100"
            >
              <el-avatar 
                :size="32" 
                :src="reply.authorAvatar"
                class="flex-shrink-0"
              >
                <el-icon :size="16"><User /></el-icon>
              </el-avatar>
              
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-semibold text-sm text-gray-900">{{ reply.author }}</span>
                  <el-tag v-if="reply.isInstructor" type="warning" size="small">Преподаватель</el-tag>
                  <span class="text-xs text-gray-500">{{ formatTimestamp(reply.timestamp) }}</span>
                </div>
                <p class="text-sm text-gray-700 leading-relaxed">{{ reply.content }}</p>
              </div>
            </div>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>

    <!-- Empty State -->
    <el-empty 
      v-else
      description="Пока нет комментариев. Будьте первым!"
      :image-size="120"
    >
      <el-button type="primary" @click="showCommentForm = true">
        Добавить комментарий
      </el-button>
    </el-empty>

    <!-- Load More -->
    <div v-if="hasMore" class="text-center mt-6">
      <el-button @click="loadMore" :loading="loading">
        Загрузить еще
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  Edit, 
  Delete, 
  Warning, 
  MoreFilled,
  Star,
  ChatDotRound,
  Close
} from '@element-plus/icons-vue'

const props = defineProps({
  comments: {
    type: Array,
    default: () => []
  },
  lessonId: {
    type: String,
    required: true
  },
  topicId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['add-comment', 'reply-comment', 'edit-comment', 'delete-comment', 'like-comment'])

// State
const showCommentForm = ref(false)
const newComment = ref('')
const replyFormVisible = ref({})
const replyTexts = ref({})
const showReplies = ref({})
const loading = ref(false)
const hasMore = ref(false)

// Computed
const sortedComments = computed(() => {
  return [...props.comments].sort((a, b) => {
    return new Date(b.timestamp) - new Date(a.timestamp)
  })
})

// Methods
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'только что'
  if (minutes < 60) return `${minutes} мин назад`
  if (hours < 24) return `${hours} ч назад`
  if (days < 7) return `${days} дн назад`
  
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const submitComment = () => {
  if (!newComment.value.trim()) return
  
  emit('add-comment', {
    content: newComment.value.trim(),
    lessonId: props.lessonId,
    topicId: props.topicId
  })
  
  newComment.value = ''
  showCommentForm.value = false
}

const toggleReplyForm = (commentId) => {
  replyFormVisible.value[commentId] = !replyFormVisible.value[commentId]
  if (!replyFormVisible.value[commentId]) {
    replyTexts.value[commentId] = ''
  }
}

const submitReply = (commentId) => {
  const content = replyTexts.value[commentId]?.trim()
  if (!content) return
  
  emit('reply-comment', {
    commentId,
    content
  })
  
  replyTexts.value[commentId] = ''
  replyFormVisible.value[commentId] = false
  showReplies.value[commentId] = true
}

const toggleReplies = (commentId) => {
  showReplies.value[commentId] = !showReplies.value[commentId]
}

const likeComment = (commentId) => {
  emit('like-comment', commentId)
}

const handleCommentAction = async ({ action, commentId }) => {
  switch (action) {
    case 'edit':
      // TODO: Implement edit
      ElMessage.info('Функция редактирования в разработке')
      break
      
    case 'delete':
      try {
        await ElMessageBox.confirm(
          'Вы уверены, что хотите удалить этот комментарий?',
          'Подтверждение удаления',
          {
            confirmButtonText: 'Удалить',
            cancelButtonText: 'Отмена',
            type: 'warning'
          }
        )
        emit('delete-comment', commentId)
        ElMessage.success('Комментарий удален')
      } catch {
        // Cancelled
      }
      break
      
    case 'report':
      ElMessage.info('Жалоба отправлена модераторам')
      break
  }
}

const loadMore = () => {
  loading.value = true
  // TODO: Implement pagination
  setTimeout(() => {
    loading.value = false
    hasMore.value = false
  }, 1000)
}
</script>

<style scoped>
.comment-form-card {
  border: 2px solid #e5e7eb;
}

.comment-card {
  transition: all 0.3s ease;
}

.comment-card:hover {
  transform: translateY(-2px);
}

:deep(.el-card__body) {
  padding: 16px;
}
</style>

