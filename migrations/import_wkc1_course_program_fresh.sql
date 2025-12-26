-- ============================================================================
-- ПОЛНЫЙ ИМПОРТ ПРОГРАММЫ КУРСА ДЛЯ СТАНЦИИ WKC-1
-- ============================================================================
-- Удаляет все старые данные и создает новую программу
-- Модуль: 1. Компрессорная станция WKC-1
-- ============================================================================

DO $$
DECLARE
    v_station_id INTEGER := 1; -- WKC1
    v_program_id INTEGER;
    v_lesson_id INTEGER;
BEGIN
    -- Находим существующую программу или создаем новую
    SELECT id INTO v_program_id FROM course_programs 
    WHERE station_id = v_station_id AND title = 'Компрессорная станция WKC-1' LIMIT 1;
    
    -- Удаляем ВСЕ старые данные программы (каскадное удаление)
    IF v_program_id IS NOT NULL THEN
        -- Удаляем в правильном порядке (из-за внешних ключей)
        DELETE FROM course_program_topic_files WHERE course_program_topic_id IN (
            SELECT id FROM course_program_topics WHERE course_program_lesson_id IN (
                SELECT id FROM course_program_lessons WHERE course_program_id = v_program_id
            )
        );
        DELETE FROM course_program_topics WHERE course_program_lesson_id IN (
            SELECT id FROM course_program_lessons WHERE course_program_id = v_program_id
        );
        DELETE FROM course_program_lesson_tests WHERE course_program_lesson_id IN (
            SELECT id FROM course_program_lessons WHERE course_program_id = v_program_id
        );
        DELETE FROM course_program_lessons WHERE course_program_id = v_program_id;
        DELETE FROM course_program_learning_outcomes WHERE course_program_id = v_program_id;
        DELETE FROM course_program_requirements WHERE course_program_id = v_program_id;
        DELETE FROM course_program_target_audience WHERE course_program_id = v_program_id;
        DELETE FROM final_tests WHERE course_program_id = v_program_id;
        DELETE FROM course_programs WHERE id = v_program_id;
    END IF;
    
    -- Создаем новую программу курса
    INSERT INTO course_programs (
        station_id,
        title,
        description,
        duration,
        topics_count,
        lessons_count,
        tests_count,
        format,
        is_active,
        order_index
    ) VALUES (
        v_station_id,
        'Компрессорная станция WKC-1',
        'Программа обучения по компрессорной станции WKC-1',
        '40 часов',
        39, -- Всего тем (4+21+10+4)
        4,  -- Всего уроков
        4,  -- Тесты к каждому уроку
        'Онлайн',
        true,
        0
    ) RETURNING id INTO v_program_id;

    -- ========================================================================
    -- Блоки для фронтенда/админки: Что вы изучите / Требования / Целевая аудитория
    -- ========================================================================
    INSERT INTO course_program_learning_outcomes (course_program_id, outcome_text, order_index) VALUES
    (v_program_id, 'Обзор технологического процесса компрессорной станции WKC-1 и ключевых зон', 0),
    (v_program_id, 'Оборудование зоны замера газа: расходомеры, вычислители, анализ газа, системы мониторинга', 1),
    (v_program_id, 'Устройство и работа ГПА: управление, смазка, компрессор, топливный газ, уплотнения, антипомпаж', 2),
    (v_program_id, 'Вспомогательные системы станции: очистка, АВО, воздух, теплоснабжение, ЭХЗ, арматура, ПБ', 3),
    (v_program_id, 'Базовые алгоритмы запуска/останова ГПА и принципы безопасной эксплуатации', 4);

    INSERT INTO course_program_requirements (course_program_id, requirement_text, order_index) VALUES
    (v_program_id, 'Базовые знания техники безопасности и охраны труда', 0),
    (v_program_id, 'Понимание основ эксплуатации промышленного оборудования (желательно)', 1),
    (v_program_id, 'Доступ к ПК/планшету и интернету для прохождения онлайн-тренинга', 2);

    INSERT INTO course_program_target_audience (course_program_id, audience_text, order_index) VALUES
    (v_program_id, 'Операторы/машинисты и сменный персонал компрессорных станций', 0),
    (v_program_id, 'Инженеры КИПиА/АСУ ТП, энергетики, механики, специалисты по обслуживанию', 1),
    (v_program_id, 'Новые сотрудники и стажёры, проходящие вводное обучение по WKC-1', 2);
    
    -- ========================================================================
    -- УРОК № 1: Зона замера газа
    -- ========================================================================
    INSERT INTO course_program_lessons (
        course_program_id,
        lesson_key,
        title,
        duration,
        order_index,
        is_active
    ) VALUES (
        v_program_id,
        'wkc1-lesson-1',
        'Урок № 1. Зона замера газа',
        '2 часа',
        1,
        true
    ) RETURNING id INTO v_lesson_id;
    
    -- Темы урока 1
    INSERT INTO course_program_topics (course_program_lesson_id, topic_key, code, title, duration, order_index, is_active) VALUES
    (v_lesson_id, 'wkc1-lesson-1-topic-1', '1.1', 'Ультразвуковые расходомеры', '30 мин', 1, true),
    (v_lesson_id, 'wkc1-lesson-1-topic-2', '1.2', 'Вычислители расхода газа', '30 мин', 2, true),
    (v_lesson_id, 'wkc1-lesson-1-topic-3', '1.3', 'Кабина анализа газа', '30 мин', 3, true),
    (v_lesson_id, 'wkc1-lesson-1-topic-4', '1.4', 'Система СBM', '30 мин', 4, true);
    
    -- Тест к уроку 1
    INSERT INTO course_program_lesson_tests (course_program_lesson_id, title, questions_count, is_active) VALUES
    (v_lesson_id, 'Тестовые задания к Уроку 1', 10, true);
    
    -- ========================================================================
    -- УРОК № 2: Зона Компримирование (ГПА)
    -- ========================================================================
    INSERT INTO course_program_lessons (
        course_program_id,
        lesson_key,
        title,
        duration,
        order_index,
        is_active
    ) VALUES (
        v_program_id,
        'wkc1-lesson-2',
        'Урок № 2. Зона Компримирование (ГПА)',
        '10 часов',
        2,
        true
    ) RETURNING id INTO v_lesson_id;
    
    -- Темы урока 2
    INSERT INTO course_program_topics (course_program_lesson_id, topic_key, code, title, duration, order_index, is_active) VALUES
    (v_lesson_id, 'wkc1-lesson-2-topic-1', '2.1', 'Система управления ГПА', '30 мин', 1, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-2', '2.2', 'Система смазки ГПА', '30 мин', 2, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-3', '2.3', 'Центробежный компрессор (Нагнетатель)', '30 мин', 3, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-4', '2.4', 'Система топливного газа ГПА', '30 мин', 4, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-5', '2.5', 'Углекислотная система пожаратушения', '30 мин', 5, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-6', '2.6', 'Система Сухого газовога уплотнения ЦБН', '30 мин', 6, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-7', '2.7', 'Регламентные работы на ГПА', '30 мин', 7, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-8', '2.8', 'Силовая турбина ГПА', '30 мин', 8, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-9', '2.9', 'Электроснабжения ГПА', '30 мин', 9, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-10', '2.10', 'Газогенератор ГПА', '30 мин', 10, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-11', '2.11', 'Система аварийного электроснабжения ГПА', '30 мин', 11, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-12', '2.12', 'Гидравлическая система Запуска ГПА', '30 мин', 12, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-13', '2.13', 'Антипомпажная система ГПА', '30 мин', 13, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-14', '2.14', 'Система контроля вибрации ГПА', '30 мин', 14, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-15', '2.15', 'Воздушно очистетельное устройство (ВОУ) и шахта отработанных газов ГПА', '30 мин', 15, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-16', '2.16', 'Промывка ГПА', '30 мин', 16, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-17', '2.17', 'Система бустерного газа', '30 мин', 17, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-18', '2.18', 'Система пожаратушения цеха ГПА', '30 мин', 18, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-19', '2.19', 'Алгоритм запуска и останова ГПА GE', '30 мин', 19, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-20', '2.20', 'Алгоритм запуска и останова ГПА Solar', '30 мин', 20, true),
    (v_lesson_id, 'wkc1-lesson-2-topic-21', '2.21', 'Пуск и остонов ГПА SOLAR', '30 мин', 21, true);
    
    -- Тест к уроку 2
    INSERT INTO course_program_lesson_tests (course_program_lesson_id, title, questions_count, is_active) VALUES
    (v_lesson_id, 'Тестовые задания к Уроку 2', 20, true);
    
    -- ========================================================================
    -- УРОК № 3: Вспомогательное оборудование WKC-1
    -- ========================================================================
    INSERT INTO course_program_lessons (
        course_program_id,
        lesson_key,
        title,
        duration,
        order_index,
        is_active
    ) VALUES (
        v_program_id,
        'wkc1-lesson-3',
        'Урок № 3. Вспомогательное оборудование WKC-1',
        '5 часов',
        3,
        true
    ) RETURNING id INTO v_lesson_id;
    
    -- Темы урока 3
    INSERT INTO course_program_topics (course_program_lesson_id, topic_key, code, title, duration, order_index, is_active) VALUES
    (v_lesson_id, 'wkc1-lesson-3-topic-1', '3.1', 'Зона очистки газа', '30 мин', 1, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-2', '3.2', 'Блок подготовки топливного газа', '30 мин', 2, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-3', '3.3', 'Зона АВО газа', '30 мин', 3, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-4', '3.4', 'Компрессор сжатого воздуха', '30 мин', 4, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-5', '3.5', 'Система теплоснабжения', '30 мин', 5, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-6', '3.6', 'Противопожарная система', '30 мин', 6, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-7', '3.7', 'Запорные арматуры', '30 мин', 7, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-8', '3.8', 'Система замера газа станции КС1', '30 мин', 8, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-9', '3.9', 'Система ЭХЗ', '30 мин', 9, true),
    (v_lesson_id, 'wkc1-lesson-3-topic-10', '3.10', 'Система смазки газогенератора Jenbacher', '30 мин', 10, true);
    
    -- Тест к уроку 3
    INSERT INTO course_program_lesson_tests (course_program_lesson_id, title, questions_count, is_active) VALUES
    (v_lesson_id, 'Тестовые задания к Уроку 3', 15, true);
    
    -- ========================================================================
    -- УРОК № 4: ГПЭС
    -- ========================================================================
    INSERT INTO course_program_lessons (
        course_program_id,
        lesson_key,
        title,
        duration,
        order_index,
        is_active
    ) VALUES (
        v_program_id,
        'wkc1-lesson-4',
        'Урок № 4. ГПЭС',
        '2 часа',
        4,
        true
    ) RETURNING id INTO v_lesson_id;
    
    -- Темы урока 4
    INSERT INTO course_program_topics (course_program_lesson_id, topic_key, code, title, duration, order_index, is_active) VALUES
    (v_lesson_id, 'wkc1-lesson-4-topic-1', '4.1', 'Газогенератора «GE Jenbacher»', '30 мин', 1, true),
    (v_lesson_id, 'wkc1-lesson-4-topic-2', '4.2', 'Система электроснабжения', '30 мин', 2, true),
    (v_lesson_id, 'wkc1-lesson-4-topic-3', '4.3', 'Противопожарная система', '30 мин', 3, true),
    (v_lesson_id, 'wkc1-lesson-4-topic-4', '4.4', 'Дополнительные системы', '30 мин', 4, true);
    
    -- Тест к уроку 4
    INSERT INTO course_program_lesson_tests (course_program_lesson_id, title, questions_count, is_active) VALUES
    (v_lesson_id, 'Тестовые задания к Уроку 4', 10, true);
    
    -- Обновляем счетчики в программе
    UPDATE course_programs SET
        topics_count = (SELECT COUNT(*) FROM course_program_topics WHERE course_program_lesson_id IN (
            SELECT id FROM course_program_lessons WHERE course_program_id = v_program_id
        )),
        lessons_count = (SELECT COUNT(*) FROM course_program_lessons WHERE course_program_id = v_program_id),
        tests_count = (SELECT COUNT(*) FROM course_program_lesson_tests WHERE course_program_lesson_id IN (
            SELECT id FROM course_program_lessons WHERE course_program_id = v_program_id
        )),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = v_program_id;
    
    RAISE NOTICE 'Программа курса для WKC-1 успешно создана. Program ID: %', v_program_id;
END $$;

