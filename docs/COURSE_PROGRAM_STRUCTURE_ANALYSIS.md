# Анализ структуры программы курса

## Структура данных, ожидаемая фронтендом

### 1. Структура CourseProgram (из `_serialize_course_program`)

```javascript
{
  id: number,
  stationId: number,
  title: string,
  description: string,
  duration: string,
  format: string,
  isActive: boolean,
  orderIndex: number,
  topicsCount: number,
  lessonsCount: number,
  testsCount: number,
  learningOutcomes: string[],
  requirements: string[],
  targetAudience: string[],
  finalTest: {
    title: string,
    questionsCount: number
  } | null,
  lessons: [
    {
      id: number,
      lessonKey: string,        // Уникальный ключ урока (например: "wkc1-lesson-1")
      title: string,            // Название урока (например: "Урок № 1. Зона замера газа")
      duration: string,         // Длительность (например: "2 часа")
      orderIndex: number,       // Порядок отображения
      topics: [
        {
          id: number,
          topicKey: string,     // Уникальный ключ темы (например: "wkc1-lesson-1-topic-1")
          code: string,         // Код темы (например: "1.1")
          title: string,        // Название темы
          duration: string,     // Длительность (например: "30 мин")
          orderIndex: number,   // Порядок отображения
          files: [              // Файлы материалов темы
            {
              id: number,
              title: string,
              originalName: string,
              objectKey: string,  // Ключ в MinIO
              fileType: string,   // Тип файла
              isMain: boolean,    // Основной файл
              orderIndex: number,
              fileSize: number,
              mimeType: string
            }
          ]
        }
      ],
      test: {                   // ⚠️ ОЖИДАЕТСЯ, НО ОТСУТСТВУЕТ В БД
        title: string,
        questionsCount: number
      } | null
    }
  ]
}
```

## Проблемы текущей структуры БД

### ❌ Отсутствует таблица для тестов к урокам

**Фронтенд ожидает:**
- `lesson.test` - тест для каждого урока (например: "Тестовые задания к Уроку 1")

**Текущая БД:**
- ✅ `final_tests` - итоговые тесты для программы (связаны с `course_program_id`)
- ❌ НЕТ таблицы для тестов к `course_program_lessons`

### ✅ Существующие таблицы (корректные)

1. **course_programs** - программы курсов
2. **course_program_lessons** - уроки программы
3. **course_program_topics** - темы уроков
4. **course_program_topic_files** - файлы материалов тем
5. **final_tests** - итоговые тесты программы

## Рекомендуемая структура БД

### Новая таблица: `course_program_lesson_tests`

```sql
CREATE TABLE IF NOT EXISTS course_program_lesson_tests (
    id SERIAL PRIMARY KEY,
    course_program_lesson_id INTEGER NOT NULL REFERENCES course_program_lessons(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    questions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lesson_tests_lesson 
ON course_program_lesson_tests(course_program_lesson_id);
```

## Формат данных для фронтенда

### Урок (Lesson)
```typescript
interface Lesson {
  id: number
  lessonKey: string           // Уникальный ключ: "wkc1-lesson-1"
  title: string               // "Урок № 1. Зона замера газа"
  duration: string            // "2 часа"
  orderIndex: number          // 1, 2, 3...
  topics: Topic[]             // Массив тем
  test: LessonTest | null      // Тест к уроку (ОБЯЗАТЕЛЬНО!)
}

interface Topic {
  id: number
  topicKey: string            // Уникальный ключ: "wkc1-lesson-1-topic-1"
  code: string                // "1.1", "1.2"...
  title: string               // "Ультразвуковые расходомеры"
  duration: string            // "30 мин"
  orderIndex: number          // 1, 2, 3...
  files: TopicFile[]          // Файлы материалов
}

interface LessonTest {
  title: string               // "Тестовые задания к Уроку 1"
  questionsCount: number      // 10, 20...
}
```

## Что нужно сделать

1. ✅ Создать таблицу `course_program_lesson_tests`
2. ✅ Обновить функцию `_serialize_course_program` для включения тестов уроков
3. ✅ Обновить импорт данных WKC-1 для добавления тестов к урокам
4. ✅ Обновить модель Django для новой таблицы

