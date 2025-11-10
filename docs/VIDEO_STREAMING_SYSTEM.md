# 🎥 Система видеоплеера и streaming

## 📋 Обзор

Полная система для воспроизведения видеоуроков с:
- Боковым меню уроков
- Модальным видеоплеером
- Интеграцией с Supabase
- Сохранением прогресса
- Переключением между уроками

## 🎬 Возможности

### 1. Боковое меню уроков
- ✅ Список всех уроков курса
- ✅ Отображение номера и статуса (завершено/не завершено)
- ✅ Клик для воспроизведения
- ✅ Активный урок выделен
- ✅ Скроллируемый список

### 2. Модальное окно видеоплеера
- ✅ HTML5 видеоплеер
- ✅ Полноэкранный режим
- ✅ Информация об уроке
- ✅ Прогресс-бар
- ✅ Кнопки переключения уроков

### 3. Функции плеера
- ✅ Автопродолжение с сохраненной позиции
- ✅ Сохранение прогресса в Supabase
- ✅ Отметка завершения урока
- ✅ Переключение вперед/назад
- ✅ Загрузка состояния

## 📦 Установленные библиотеки

```bash
npm install vue3-video-player video.js
```

**Используется**: 
- `video.js` - мощный видеоплеер
- `@element-plus/icons-vue` - иконки

## 🗄️ Структура базы данных

### Таблицы в Supabase

#### `lessons` - Уроки
```sql
- id: UUID
- course_id: UUID (FK to courses)
- title: VARCHAR(255)
- description: TEXT
- video_url: TEXT - URL видео
- duration_minutes: INTEGER
- lesson_order: INTEGER
- lesson_type: VARCHAR(50) - video/document/quiz
- is_free: BOOLEAN
- content: TEXT
- resources: JSONB
```

#### `lesson_progress` - Прогресс
```sql
- id: UUID
- user_id: UUID (FK to users)
- lesson_id: UUID (FK to lessons)
- progress_percent: INTEGER
- watch_time_seconds: INTEGER
- last_position_seconds: INTEGER - Последняя позиция воспроизведения
- completed: BOOLEAN
- completed_at: TIMESTAMP
- last_activity: TIMESTAMP
```

## 🔧 API сервиса `videoService.js`

### Основные методы

#### `uploadVideo(file, lessonId)`
Загрузить видео в Supabase Storage:
```javascript
await videoService.uploadVideo(file, lessonId)
// { success: true, url: 'https://...' }
```

#### `getVideoUrl(lessonId)`
Получить URL видео:
```javascript
const result = await videoService.getVideoUrl(lessonId)
// { success: true, url: 'https://...' }
```

#### `saveProgress(userId, lessonId, progress)`
Сохранить прогресс:
```javascript
await videoService.saveProgress(userId, lessonId, 75) // 75%
```

#### `completeLesson(userId, lessonId)`
Отметить урок как завершенный:
```javascript
await videoService.completeLesson(userId, lessonId)
```

#### `getLessonProgress(userId, lessonId)`
Получить прогресс урока:
```javascript
const result = await videoService.getLessonProgress(userId, lessonId)
// { success: true, progress: 75 }
```

## 📹 Использование видеоплеера

### В CourseDetail.vue

```vue
<VideoPlayer
  v-model="showVideoPlayer"
  :video-url="currentLesson?.videoUrl || ''"
  :video-title="currentLesson?.title || ''"
  :video-description="currentLesson?.sectionTitle || ''"
  :video-id="currentLesson?.id"
  :lessons="allLessons"
  :current-index="currentLessonIndex"
  @video-end="handleVideoEnd"
  @close="handleVideoClose"
  @next="playNext"
  @previous="playPrevious"
/>
```

## 🎥 Streaming видео через Supabase

### Вариант 1: Прямое воспроизведение (рекомендуется)
```
<video src="https://your-project.supabase.co/storage/v1/object/public/videos/lesson-1.mp4" />
```

### Вариант 2: Progressive Download
Видео загружается частями, автоматически обрабатывается браузером.

### Вариант 3: HLS / DASH (для больших файлов)
Можно использовать библиотеки:
- HLS.js для HLS streaming
- Shaka Player для DASH/HLS

## 📊 Сохранение прогресса

### Автоматическое сохранение
```javascript
// В VideoPlayer.vue
@timeupdate="handleTimeUpdate"

handleTimeUpdate = () => {
  const progress = (currentTime / duration) * 100
  // Сохраняем каждые 10 секунд
  if (Date.now() - lastSave > 10000) {
    videoService.saveProgress(userId, lessonId, progress)
  }
}
```

### При завершении урока
```javascript
@ended="handleEnd"

handleEnd = () => {
  videoService.completeLesson(userId, lessonId)
  emit('video-end', videoId)
}
```

## 🚀 Установка и настройка

### 1. Установить зависимости
```bash
npm install vue3-video-player video.js
```

### 2. Создать bucket в Supabase
1. Откройте Supabase Dashboard
2. Storage → New bucket
3. Имя: `videos`
4. Public: ✅ Yes

### 3. Загрузить видео
```javascript
const result = await videoService.uploadVideo(file, lessonId)
if (result.success) {
  // Видео загружено
  console.log('Video URL:', result.url)
}
```

## 🎨 Визуальные особенности

### Боковое меню
- Компактный дизайн
- Автопрокрутка к активному уроку
- Hover-эффекты
- Статус завершения (зеленая галочка)
- Разделение по секциям курса

### Модальное окно
- Адаптивный размер (90% ширины экрана)
- Прогресс-бар под видео
- Кнопки навигации
- Кнопка закрытия
- Затемненный фон

## 📱 Responsive

### Desktop
- Модальное окно 1200px
- Полный функционал
- Горизонтальные кнопки

### Mobile
- Модальное окно 95% ширины
- Вертикальные кнопки
- Touch-friendly controls

## 🔐 Безопасность

### Supabase RLS
```sql
-- Разрешить публичный доступ к видео
CREATE POLICY "Public video access"
ON storage.objects
FOR SELECT
USING (bucket_id = 'videos');
```

### Проверка доступа
```javascript
// Проверяем доступ к уроку
if (lesson.is_free || user.hasAccess(courseId)) {
  playLesson()
}
```

## 💡 Оптимизация загрузки

### Lazy Loading
Видео загружается только при открытии:
```javascript
const playLesson = async (index) => {
  // Загружаем URL только сейчас
  const videoUrl = await videoService.getVideoUrl(lessonId)
  currentLesson.value.videoUrl = videoUrl
  showVideoPlayer.value = true
}
```

### Preload
```vue
<video 
  :src="videoUrl"
  preload="metadata" <!-- Не загружаем все видео сразу -->
/>
```

## 🎯 Будущие улучшения

- [ ] Subtitles support (SRT/VTT)
- [ ] Multiple video qualities
- [ ] Picture-in-Picture mode
- [ ] Keyboard shortcuts
- [ ] Bookmarks
- [ ] Speed control
- [ ] Volume control memory
- [ ] Playback history

---
**Дата создания**: 23 января 2025  
**Статус**: ✅ Готово  
**Версия**: 1.0


