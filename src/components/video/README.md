# Educational Video Player

Универсальный видеоплеер для образовательных платформ с поддержкой streaming API и функций, используемых на других образовательных сайтах.

## Особенности

- ✅ **Streaming API** - Использует `/api/files/video/` для эффективного стриминга с Range Requests
- ✅ **Plyr Integration** - Профессиональный видеоплеер с современным UI
- ✅ **Автосохранение прогресса** - Автоматически сохраняет и восстанавливает позицию просмотра
- ✅ **Скорость воспроизведения** - Поддержка изменения скорости (0.5x - 2x)
- ✅ **Качество видео** - Переключение качества для HLS потоков
- ✅ **Полноэкранный режим** - Нативный полноэкранный режим
- ✅ **Адаптивный дизайн** - Работает на всех устройствах
- ✅ **Обработка ошибок** - Понятные сообщения об ошибках с возможностью повтора

## Использование

### Базовый пример

```vue
<template>
  <EducationalVideoPlayer
    :source="videoSource"
    @ready="onPlayerReady"
    @timeupdate="onTimeUpdate"
  />
</template>

<script setup>
import { ref } from 'vue'
import EducationalVideoPlayer from '@/components/video/EducationalVideoPlayer.vue'

const videoSource = ref({
  objectKey: 'videos/course/lesson1.mp4',
  title: 'Урок 1: Введение'
})
</script>
```

### С URL напрямую

```vue
<EducationalVideoPlayer
  source="/api/files/video/videos/my-video.mp4"
/>
```

### С объектом из API

```vue
<EducationalVideoPlayer
  :source="{
    objectKey: file.objectKey,
    url: file.url,
    title: file.originalName,
    mimeType: file.mimeType
  }"
  :poster="posterUrl"
  :start-time="savedProgress"
  :save-progress="true"
  :progress-key="`lesson_${lessonId}`"
/>
```

### С аутентификацией

```vue
<EducationalVideoPlayer
  :source="videoSource"
  :require-auth="true"
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `source` | `String \| Object` | **required** | URL видео или объект с информацией о видео |
| `poster` | `String` | `null` | URL постера (превью изображения) |
| `requireAuth` | `Boolean` | `false` | Требуется ли аутентификация |
| `preload` | `String` | `'metadata'` | Стратегия предзагрузки: `'none'`, `'metadata'`, `'auto'` |
| `autoplay` | `Boolean` | `false` | Автовоспроизведение |
| `startTime` | `Number` | `0` | Начальное время воспроизведения (секунды) |
| `containerClass` | `String` | `''` | Дополнительные CSS классы |
| `containerStyle` | `Object` | `{}` | Стили контейнера |
| `showQuality` | `Boolean` | `true` | Показывать настройки качества |
| `showSpeed` | `Boolean` | `true` | Показывать настройки скорости |
| `speedOptions` | `Array` | `[0.5, 0.75, 1, 1.25, 1.5, 2]` | Доступные скорости |
| `saveProgress` | `Boolean` | `true` | Сохранять прогресс в localStorage |
| `progressKey` | `String` | `null` | Ключ для сохранения прогресса |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `ready` | `player` | Плеер готов к использованию |
| `play` | - | Воспроизведение начато |
| `pause` | - | Воспроизведение приостановлено |
| `ended` | - | Видео завершено |
| `timeupdate` | `time` | Обновление времени (секунды) |
| `progress` | `percent` | Прогресс загрузки буфера (%) |
| `error` | `error` | Ошибка воспроизведения |
| `fullscreen-change` | `isFullscreen` | Изменение полноэкранного режима |
| `quality-change` | `quality` | Изменение качества |
| `speed-change` | `speed` | Изменение скорости |

## Методы

Компонент предоставляет следующие методы через `ref`:

```vue
<template>
  <EducationalVideoPlayer
    ref="player"
    :source="videoSource"
  />
  <button @click="player.play()">Play</button>
  <button @click="player.pause()">Pause</button>
  <button @click="player.seek(120)">Seek to 2:00</button>
</template>

<script setup>
import { ref } from 'vue'
const player = ref(null)
</script>
```

### Доступные методы:

- `play()` - Начать воспроизведение
- `pause()` - Приостановить воспроизведение
- `stop()` - Остановить воспроизведение
- `seek(time)` - Перейти к времени (секунды)
- `setVolume(volume)` - Установить громкость (0-1)
- `toggleMute()` - Переключить звук
- `enterFullscreen()` - Войти в полноэкранный режим
- `exitFullscreen()` - Выйти из полноэкранного режима
- `loadProgress()` - Загрузить сохраненный прогресс
- `clearProgress()` - Очистить сохраненный прогресс

## Примеры использования

### Интеграция с курсом

```vue
<template>
  <div class="lesson-viewer">
    <EducationalVideoPlayer
      :source="currentLesson.video"
      :poster="currentLesson.poster"
      :start-time="lessonProgress"
      :progress-key="`lesson_${currentLesson.id}`"
      @timeupdate="saveLessonProgress"
      @ended="onLessonComplete"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import EducationalVideoPlayer from '@/components/video/EducationalVideoPlayer.vue'

const currentLesson = ref({
  id: 1,
  video: { objectKey: 'videos/lesson1.mp4' },
  poster: 'posters/lesson1.jpg'
})

const lessonProgress = computed(() => {
  const saved = localStorage.getItem(`lesson_${currentLesson.value.id}`)
  return saved ? parseFloat(saved) : 0
})

const saveLessonProgress = (time) => {
  // Дополнительная логика сохранения на сервер
  api.saveProgress(currentLesson.value.id, time)
}

const onLessonComplete = () => {
  // Отметить урок как завершенный
  api.completeLesson(currentLesson.value.id)
}
</script>
```

### Промо-видео станции

```vue
<template>
  <EducationalVideoPlayer
    :source="promoVideo.objectKey"
    :poster="stationImage"
    autoplay
    :show-quality="false"
  />
</template>
```

## Streaming API

Плеер автоматически использует streaming API (`/api/files/video/`) для эффективного стриминга с поддержкой Range Requests. Это позволяет:

- Начинать воспроизведение до полной загрузки
- Перематывать видео без полной загрузки
- Экономить трафик при просмотре части контента

## Совместимость

- ✅ Chrome/Edge (последние версии)
- ✅ Firefox (последние версии)
- ✅ Safari (последние версии)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Зависимости

- `plyr` - Видеоплеер библиотека
- `@/services/videoStreamService` - Сервис для работы с streaming API

