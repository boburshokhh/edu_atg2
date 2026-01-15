<template>
  <el-dialog
    v-model="dialogVisible"
    width="90%"
    class="max-w-lg"
    align-center
    destroy-on-close
  >
    <template #header>
      <div class="flex flex-col gap-1">
        <h3 class="text-lg font-semibold text-gray-900">
          Начать обучение
        </h3>
        <p class="text-sm text-gray-500">
          {{ courseProgram?.title || 'Программа курса' }}
        </p>
      </div>
    </template>

    <div class="space-y-4">
      <div class="rounded-lg border border-blue-100 bg-blue-50 p-4 text-sm text-gray-700">
        <p class="font-medium text-blue-700 mb-2">Что будет дальше</p>
        <ul class="list-disc list-inside space-y-1">
          <li>Курс добавится в ваш профиль</li>
          <li>Прогресс будет сохраняться автоматически</li>
          <li>Вы сможете продолжить обучение с любого устройства</li>
        </ul>
      </div>

      <div v-if="isFirstEnrollment" class="space-y-3">
        <p class="text-sm text-gray-700">
          Перед стартом подтвердите согласие с правилами обучения и политикой доступа к материалам.
        </p>
        <el-checkbox v-model="consentChecked">
          Я согласен(а) с условиями обучения
        </el-checkbox>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="handleClose" :disabled="loading">
          Отмена
        </el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleConfirm"
        >
          Начать обучение
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'EnrollCourseModal',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    courseProgram: {
      type: Object,
      default: null
    },
    isFirstEnrollment: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'confirm'],
  setup(props, { emit }) {
    const consentChecked = ref(false)
    const dialogVisible = computed({
      get() {
        return props.modelValue
      },
      set(value) {
        emit('update:modelValue', value)
      }
    })

    watch(
      () => props.modelValue,
      (value) => {
        if (!value) {
          consentChecked.value = false
        }
      }
    )

    const handleClose = () => {
      dialogVisible.value = false
    }

    const handleConfirm = () => {
      if (props.isFirstEnrollment && !consentChecked.value) {
        ElMessage.warning('Подтвердите согласие перед началом обучения')
        return
      }
      emit('confirm')
    }

    return {
      dialogVisible,
      consentChecked,
      handleClose,
      handleConfirm
    }
  }
}
</script>
