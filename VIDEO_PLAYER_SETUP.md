# Видеоплеер для образовательной платформы

## ✅ Что реализовано

### 1. Streaming API с Range Requests
- **Backend**: `/api/files/video/<key>` - публичный streaming endpoint
- **Backend**: `/api/files/stream/<key>` - защищенный streaming endpoint (требует аутентификации)
- **Backend**: `/api/files/hls/<key>` - HLS streaming endpoint
- Поддержка HTTP Range Requests для частичной загрузки видео
- Оптимизированные заголовки кэширования

### 2. EducationalVideoPlayer компонент
- **Расположение**: `src/components/video/EducationalVideoPlayer.vue`
- **Особенности**:
  - ✅ Интеграция с Plyr (профессиональный видеоплеер)
  - ✅ Автоматическое использование streaming API
  - ✅ Автосохранение прогресса просмотра
  - ✅ Настройки скорости воспроизведения (0.5x - 2x)
  - ✅ Переключение качества (для HLS)
  - ✅ Полноэкранный режим
  - ✅ Адаптивный дизайн
  - ✅ Обработка ошибок с возможностью повтора

### 3. VideoStreamService
- **Расположение**: `src/services/videoStreamService.js`
- **Функции**:
  - `getVideoStreamUrl()` - получение streaming URL
  - `getHlsStreamUrl()` - получение HLS URL
  - `createVideoSource()` - создание источника для Plyr
  - `convertToStreamUrl()` - конвертация presigned URL в streaming URL

## 📖 Использование

### Базовый пример

```vue
<template>
  <EducationalVideoPlayer
    :source="videoSource"
  />
</template>

<script setup>
import EducationalVideoPlayer from '@/components/video/EducationalVideoPlayer.vue'

const videoSource = {
  objectKey: 'videos/course/lesson1.mp4',
  title: 'Урок 1'
}
</script>
```

### С объектом из API

```vue
<EducationalVideoPlayer
  :source="{
    objectKey: file.objectKey,
    url: file.url,
    title: file.originalName
  }"
  :save-progress="true"
  :progress-key="`lesson_${lessonId}`"
  @timeupdate="onTimeUpdate"
/>
```

### С URL напрямую

```vue
<EducationalVideoPlayer
  source="/api/files/video/videos/my-video.mp4"
/>
```

## 🔧 Интеграция

### Обновлен ContentViewer
Компонент `src/components/lesson/ContentViewer.vue` теперь использует `EducationalVideoPlayer` вместо `OptimizedVideoPlayer`.

### Миграция существующих компонентов

Если вы используете `OptimizedVideoPlayer`, замените на:

```vue
<!-- Было -->
<OptimizedVideoPlayer :source="videoSource" />

<!-- Стало -->
<EducationalVideoPlayer :source="videoSource" />
```

## 🎯 API Endpoints

### Публичный streaming (без аутентификации)
```
GET /api/files/video/<objectKey>
```

### Защищенный streaming (требует аутентификации)
```
GET /api/files/stream/<objectKey>
```

### HLS streaming
```
GET /api/files/hls/<objectKey>
```

Все endpoints поддерживают:
- HTTP Range Requests (`Range: bytes=start-end`)
- CORS заголовки
- Оптимизированное кэширование

## 🚀 Преимущества

1. **Эффективный стриминг**: Видео загружается по частям, не нужно ждать полной загрузки
2. **Быстрый старт**: Воспроизведение начинается сразу после загрузки метаданных
3. **Экономия трафика**: Загружаются только просмотренные части
4. **Перемотка без загрузки**: Можно перематывать видео без полной загрузки
5. **Автосохранение прогресса**: Пользователь может продолжить с того места, где остановился

## 📝 Примеры использования

### В уроке курса

```vue
<template>
  <EducationalVideoPlayer
    :source="currentLesson.video"
    :poster="currentLesson.poster"
    :start-time="savedProgress"
    :progress-key="`lesson_${currentLesson.id}`"
    @timeupdate="saveProgress"
    @ended="onLessonComplete"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import EducationalVideoPlayer from '@/components/video/EducationalVideoPlayer.vue'

const currentLesson = ref({
  id: 1,
  video: { objectKey: 'videos/lesson1.mp4' }
})

const savedProgress = computed(() => {
  const saved = localStorage.getItem(`lesson_${currentLesson.value.id}`)
  return saved ? parseFloat(saved) : 0
})

const saveProgress = (time) => {
  // Сохранение на сервер
  api.saveProgress(currentLesson.value.id, time)
}

const onLessonComplete = () => {
  api.completeLesson(currentLesson.value.id)
}
</script>
```

### Промо-видео станции

```vue
<EducationalVideoPlayer
  :source="promoVideo.objectKey"
  :poster="stationImage"
  autoplay
  :show-quality="false"
/>
```

## 🔒 Безопасность

- Публичные видео доступны через `/api/files/video/` без аутентификации
- Приватные видео требуют аутентификации через `/api/files/stream/`
- Все запросы проходят через backend, прямой доступ к MinIO из браузера невозможен

## 📚 Документация

Подробная документация доступна в `src/components/video/README.md`

