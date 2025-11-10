# Компонента CourseCurriculum

## Описание

Компонента `CourseCurriculum.vue` предназначена для отображения структуры курса (программы обучения). Она показывает уроки, темы и тесты в удобном формате с возможностью раскрытия/сворачивания уроков.

## Использование

### Базовый пример

```vue
<template>
  <CourseCurriculum 
    :lessons="lessons"
    :final-test="finalTest"
    @start-test="handleStartTest"
    @start-final-test="handleStartFinalTest"
  />
</template>

<script>
import CourseCurriculum from '@/components/CourseCurriculum.vue'

export default {
  components: {
    CourseCurriculum
  },
  data() {
    return {
      lessons: [
        {
          title: 'Урок № 1: Зона замера газа',
          duration: '2.5 часа',
          topics: [
            { code: 'Тема 1.1', title: 'Ультразвуковые расходомеры', duration: '35 мин' },
            { code: 'Тема 1.2', title: 'Вычислители расхода газа', duration: '40 мин' },
            { code: 'Тема 1.3', title: 'Кабина анализа газа', duration: '30 мин' },
            { code: 'Тема 1.4', title: 'Система CBM', duration: '45 мин' }
          ],
          test: {
            title: 'Тестовые задания к Уроку 1',
            questions: 10
          }
        }
      ],
      finalTest: {
        title: 'Итоговый тест',
        questions: 30
      }
    }
  },
  methods: {
    handleStartTest(test) {
      console.log('Запуск теста:', test)
      // Логика запуска теста
    },
    handleStartFinalTest(finalTest) {
      console.log('Запуск итогового теста:', finalTest)
      // Логика запуска итогового теста
    }
  }
}
</script>
```

## Props

### `lessons` (обязательный)
- **Тип:** `Array`
- **Описание:** Массив уроков курса
- **Структура урока:**
  ```javascript
  {
    title: String,           // Название урока (обязательно)
    duration: String,          // Длительность урока (опционально)
    topics: Array,            // Массив тем (обязательно)
    test: Object              // Тест урока (опционально)
  }
  ```

### `finalTest` (опциональный)
- **Тип:** `Object`
- **Описание:** Итоговый тест курса
- **Структура:**
  ```javascript
  {
    title: String,            // Название теста
    questions: Number         // Количество вопросов
  }
  ```

## Структура данных

### Урок (Lesson)
```javascript
{
  title: 'Урок № 1: Зона замера газа',
  duration: '2.5 часа',
  topics: [
    {
      code: 'Тема 1.1',        // Код темы (опционально)
      title: 'Ультразвуковые расходомеры',  // Название темы (обязательно)
      duration: '35 мин'       // Длительность темы (опционально)
    }
  ],
  test: {
    title: 'Тестовые задания к Уроку 1',
    questions: 10              // или questionsCount: 10
  }
}
```

### Тема (Topic)
```javascript
{
  code: 'Тема 1.1',            // Код темы (опционально, отображается синим цветом)
  title: 'Ультразвуковые расходомеры',  // Название темы (обязательно)
  duration: '35 мин'           // Длительность (опционально)
}
```

### Тест (Test)
```javascript
{
  title: 'Тестовые задания к Уроку 1',
  questions: 10,               // Количество вопросов
  // или
  questionsCount: 10          // Альтернативное поле
}
```

## Events

### `@start-test`
- **Описание:** Вызывается при нажатии на кнопку "Пройти тест" для урока
- **Параметры:** `test` - объект теста урока

### `@start-final-test`
- **Описание:** Вызывается при нажатии на кнопку "Начать тест" для итогового теста
- **Параметры:** `finalTest` - объект итогового теста

## Особенности

1. **Раскрытие/сворачивание уроков:** По умолчанию все уроки свернуты. При клике на заголовок урока он раскрывается/сворачивается.

2. **Статистика курса:** Компонента автоматически вычисляет статистику:
   - Количество уроков
   - Общее количество тем
   - Общее количество тестов

3. **Адаптивный дизайн:** Компонента использует Tailwind CSS и полностью адаптивна.

4. **Анимации:** Плавные анимации раскрытия/сворачивания уроков.

## Пример структуры данных для станции

```javascript
const courseProgram = {
  title: 'Программа онлайн-тренинга "Компрессорная станция WKC-1"',
  description: 'Описание курса...',
  duration: '10 академических часов',
  lessons: [
    {
      title: 'Урок № 1: Зона замера газа',
      duration: '2.5 часа',
      topics: [
        { code: 'Тема 1.1', title: 'Ультразвуковые расходомеры', duration: '35 мин' },
        { code: 'Тема 1.2', title: 'Вычислители расхода газа', duration: '40 мин' },
        { code: 'Тема 1.3', title: 'Кабина анализа газа', duration: '30 мин' },
        { code: 'Тема 1.4', title: 'Система CBM', duration: '45 мин' }
      ],
      test: {
        title: 'Тестовые задания к Уроку 1',
        questions: 10
      }
    }
  ],
  finalTest: {
    title: 'Итоговый тест',
    questions: 30
  }
}
```

## Использование в StationCourses.vue

Компонента уже интегрирована в `StationCourses.vue` и используется в табе "Программа курса":

```vue
<CourseCurriculum 
  :lessons="courseProgram?.lessons || []"
  :final-test="courseProgram?.finalTest"
  @start-test="handleStartTest"
  @start-final-test="handleStartFinalTest"
/>
```

Материалы курса (PDF, видео) отображаются отдельно в секции "Материалы курса" для авторизованных пользователей.

