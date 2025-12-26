# Структура программы курса - Анализ и реализация

## 📊 Анализ структуры данных фронтенда

### Компоненты, использующие данные программы:

1. **CourseCurriculum.vue** - отображает структуру курса
2. **LessonSidebar.vue** - боковая панель с уроками и темами
3. **LessonContentApp.vue** - основной контент урока
4. **StationCourses.vue** - страница курса станции

### Ожидаемая структура данных:

```typescript
interface CourseProgram {
  id: number
  stationId: number
  title: string
  description: string
  duration: string
  format: string
  isActive: boolean
  orderIndex: number
  topicsCount: number
  lessonsCount: number
  testsCount: number
  learningOutcomes: string[]
  requirements: string[]
  targetAudience: string[]
  finalTest: {
    title: string
    questionsCount: number
  } | null
  lessons: Lesson[]
}

interface Lesson {
  id: number
  lessonKey: string              // Уникальный ключ: "wkc1-lesson-1"
  title: string                 // "Урок № 1. Зона замера газа"
  duration: string              // "2 часа"
  orderIndex: number            // 1, 2, 3...
  topics: Topic[]
  test: LessonTest | null       // ⚠️ ОБЯЗАТЕЛЬНО для фронтенда!
}

interface Topic {
  id: number
  topicKey: string              // Уникальный ключ: "wkc1-lesson-1-topic-1"
  code: string                  // "1.1", "1.2"...
  title: string                 // "Ультразвуковые расходомеры"
  duration: string              // "30 мин"
  orderIndex: number            // 1, 2, 3...
  files: TopicFile[]            // Файлы материалов темы
}

interface LessonTest {
  title: string                 // "Тестовые задания к Уроку 1"
  questionsCount: number        // 10, 20...
}

interface TopicFile {
  id: number
  title: string
  originalName: string
  objectKey: string              // Ключ в MinIO
  fileType: string
  isMain: boolean
  orderIndex: number
  fileSize: number
  mimeType: string
}
```

## 🗄️ Структура БД (реализована)

### Таблицы:

1. **course_programs** - программы курсов
   - `id`, `station_id`, `title`, `description`, `duration`, `format`, `is_active`, `order_index`
   - `topics_count`, `lessons_count`, `tests_count` (вычисляемые)

2. **course_program_lessons** - уроки программы
   - `id`, `course_program_id`, `lesson_key` (уникальный), `title`, `duration`, `order_index`, `is_active`

3. **course_program_topics** - темы уроков
   - `id`, `course_program_lesson_id`, `topic_key` (уникальный), `code`, `title`, `duration`, `order_index`, `is_active`

4. **course_program_lesson_tests** - ⭐ НОВАЯ: тесты к урокам
   - `id`, `course_program_lesson_id`, `title`, `questions_count`, `is_active`

5. **course_program_topic_files** - файлы материалов тем
   - `id`, `course_program_topic_id`, `title`, `original_name`, `object_key`, `file_type`, `is_main`, `order_index`, `file_size`, `mime_type`, `is_active`

6. **final_tests** - итоговые тесты программы
   - `id`, `course_program_id`, `title`, `questions_count`, `is_active`

7. **course_program_learning_outcomes** - результаты обучения
8. **course_program_requirements** - требования
9. **course_program_target_audience** - целевая аудитория

## ✅ Что было исправлено:

1. ✅ Создана таблица `course_program_lesson_tests` для тестов к урокам
2. ✅ Добавлена модель `CourseProgramLessonTest` в Django
3. ✅ Обновлена функция `_serialize_course_program` для включения тестов уроков
4. ✅ Обновлена функция `StationCourseProgramUpdateView` для сохранения тестов уроков
5. ✅ Обновлен импорт данных WKC-1 для добавления тестов к урокам
6. ✅ Исправлены запросы ForeignKey (использование `lesson__id` вместо `lesson_id`)

## 📝 Формат данных для импорта

### Пример структуры урока:

```json
{
  "lessonKey": "wkc1-lesson-1",
  "title": "Урок № 1. Зона замера газа",
  "duration": "2 часа",
  "orderIndex": 1,
  "isActive": true,
  "topics": [
    {
      "topicKey": "wkc1-lesson-1-topic-1",
      "code": "1.1",
      "title": "Ультразвуковые расходомеры",
      "duration": "30 мин",
      "orderIndex": 1,
      "isActive": true
    }
  ],
  "test": {
    "title": "Тестовые задания к Уроку 1",
    "questionsCount": 10,
    "isActive": true
  }
}
```

## 🔑 Важные моменты:

1. **Уникальные ключи**: `lesson_key` и `topic_key` должны быть уникальными и стабильными
2. **Порядок**: `order_index` определяет порядок отображения
3. **Активность**: `is_active` контролирует видимость элементов
4. **Тесты уроков**: Каждый урок должен иметь тест (`lesson.test`)
5. **Файлы тем**: Хранятся в `course_program_topic_files` и связаны через `course_program_topic_id`

## 🚀 Следующие шаги:

1. Перезапустить backend для применения изменений
2. Проверить отображение программы на фронтенде
3. При необходимости обновить данные в БД через SQL-скрипты

