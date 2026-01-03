<template>
  <div class="document-error-state">
    <!-- SVG Illustration -->
    <div class="error-illustration">
      <svg
        width="120"
        height="120"
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="error-svg"
      >
        <!-- Document -->
        <rect
          x="30"
          y="20"
          width="60"
          height="80"
          rx="4"
          fill="#E5E7EB"
          stroke="#9CA3AF"
          stroke-width="2"
        />
        <!-- Document Lines -->
        <line
          x1="40"
          y1="35"
          x2="80"
          y2="35"
          stroke="#9CA3AF"
          stroke-width="2"
          stroke-linecap="round"
        />
        <line
          x1="40"
          y1="45"
          x2="80"
          y2="45"
          stroke="#9CA3AF"
          stroke-width="2"
          stroke-linecap="round"
        />
        <line
          x1="40"
          y1="55"
          x2="70"
          y2="55"
          stroke="#9CA3AF"
          stroke-width="2"
          stroke-linecap="round"
        />
        <!-- Warning Icon -->
        <circle
          cx="70"
          cy="70"
          r="15"
          fill="#FEF3C7"
          stroke="#F59E0B"
          stroke-width="2"
        />
        <path
          d="M70 63 L70 73 M70 77 L70 77.5"
          stroke="#F59E0B"
          stroke-width="2.5"
          stroke-linecap="round"
        />
      </svg>
    </div>

    <!-- Error Title -->
    <h3 class="error-title">
      Document preview unavailable
    </h3>

    <!-- Error Message -->
    <p
      v-if="error"
      class="error-message"
    >
      {{ error }}
    </p>

    <!-- File Name (if available) -->
    <p
      v-if="fileName && !error"
      class="file-name"
    >
      {{ fileName }}
    </p>

    <!-- Action Buttons -->
    <div class="error-actions">
      <!-- Download Button (only for non-PDF) -->
      <el-button
        v-if="fileType !== 'pdf' && onDownload"
        type="primary"
        :icon="Download"
        @click="handleDownload"
      >
        Download file
      </el-button>

      <!-- Reload Button -->
      <el-button
        v-if="onReload"
        :type="fileType === 'pdf' ? 'primary' : 'default'"
        :icon="Refresh"
        :plain="fileType !== 'pdf'"
        @click="handleReload"
      >
        Reload
      </el-button>
    </div>

    <!-- PDF Info Alert -->
    <el-alert
      v-if="fileType === 'pdf'"
      type="info"
      :closable="false"
      show-icon
      class="pdf-info-alert"
    >
      <template #title>
        <span>Downloading confidential PDF documents is restricted</span>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { Download, Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  error: {
    type: String,
    default: null
  },
  fileType: {
    type: String,
    default: 'unknown'
  },
  fileName: {
    type: String,
    default: null
  },
  onReload: {
    type: Function,
    default: null
  },
  onDownload: {
    type: Function,
    default: null
  }
})

const handleReload = () => {
  if (props.onReload) {
    props.onReload()
  }
}

const handleDownload = () => {
  if (props.onDownload) {
    props.onDownload()
  }
}
</script>

<style scoped>
.document-error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem 1rem;
  width: 100%;
  gap: 1rem;
}

.error-illustration {
  margin-bottom: 0.5rem;
}

.error-svg {
  opacity: 0.8;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 0.8;
    transform: translateY(0);
  }
}

.error-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  text-align: center;
}

.error-message {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
  text-align: center;
  max-width: 500px;
}

.file-name {
  font-size: 0.875rem;
  color: #9ca3af;
  margin: 0;
  text-align: center;
  max-width: 500px;
  word-break: break-word;
}

.error-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.pdf-info-alert {
  margin-top: 1rem;
  max-width: 500px;
  width: 100%;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .document-error-state {
    min-height: 300px;
    padding: 1.5rem 1rem;
    gap: 0.75rem;
  }

  .error-illustration {
    margin-bottom: 0.25rem;
  }

  .error-svg {
    width: 100px;
    height: 100px;
  }

  .error-title {
    font-size: 1.125rem;
  }

  .error-message,
  .file-name {
    font-size: 0.8125rem;
  }

  .error-actions {
    flex-direction: column;
    width: 100%;
  }

  .error-actions .el-button {
    width: 100%;
    max-width: 280px;
  }
}
</style>

