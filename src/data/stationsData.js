// Данные по всем компрессорным станциям СП ООО «ASIA TRANS GAS»
export const stationsData = {
  1: {
    id: 1,
    name: 'Компрессорная станция WKC1',
    shortName: 'WKC1',
    description: 'Головная компрессорная станция газопровода Центральной Азии – Китай. Расположена на расстоянии 10.6 км от границы между Туркменистаном и Узбекистаном.',
    image: 'WKC1.jpg',
    techMapImage: '/tex_kart/КС1 - WKC1_page-0001.jpg',
    power: '30 МВт',
    commissionDate: '2009',
    coursesCount: 8,
    status: 'active',
    location: 'Кашкадарьинская область, Миришкорский район, посёлок Кокдумалак, Республика Узбекистан',
    type: 'Головная компрессорная станция газопровода Центральной Азии – Китай',
    designCapacity: '30 млрд м³/год',
    gasPressure: '7.0 МПа (вход) / 9.81 МПа (выход)',
    distanceFromBorder: '10.6 км от границы с Туркменистаном',
    gasSupplySources: [
      'ТКС (Туркменская компрессорная станция)',
      'ТАС (Туркменская аварийная станция)'
    ],
    pipelineDiameter: '1067 мм (вход и выход)',
    inputPressure: '7.0 МПа',
    outputPressure: '9.81 МПа',
    parallelLines: 'Две нитки (А, В)',
    
    // Основное оборудование
    equipment: [
      {
        name: 'ГПА Solar',
        model: 'TITAN130 + C45-3',
        manufacturer: 'Solar Turbines (США)',
        quantity: 2,
        power: '15 МВт каждый',
        description: 'Газовая турбина TITAN130 + центробежный компрессор C45-3'
      },
      {
        name: 'ГПА GE',
        model: 'PGT25+ + PCL803',
        manufacturer: 'GE - General Electric (США)',
        quantity: 3,
        power: '30 МВт каждый',
        description: 'Газовая турбина PGT25+ + центробежный компрессор PCL803'
      },
      {
        name: 'Компрессор сжатого воздуха',
        model: 'Atlas Copco GA 132',
        manufacturer: 'Atlas Copco (Швеция)',
        quantity: 2,
        power: 'Рабочее давление: 1.0 МПа',
        description: 'Подача сжатого воздуха для системы сухого уплотнения. Производительность: 1242 м³/ч'
      },
      {
        name: 'Газогенератор',
        model: 'Jenbacher JGS420 GS-N.L',
        manufacturer: 'GE Jenbacher (Австрия)',
        quantity: 3,
        power: '1451 кВт/час каждый',
        description: 'Скорость: 1500 об/мин. Автономная электростанция'
      },
      {
        name: 'Дизель-генератор',
        model: 'Volvo Penta',
        manufacturer: 'Volvo (Швеция)',
        quantity: 1,
        power: '260 кВт/час',
        description: 'Скорость: 1500 об/мин. Для аварийного питания при останове газогенераторов'
      },
      {
        name: 'Циклонные сепараторы',
        model: 'CYC',
        manufacturer: 'Различные',
        quantity: 8,
        description: 'Удаление влаги, пыли, механических примесей. Пропускная способность: 798.35 NKm³/час'
      },
      {
        name: 'Фильтры сепараторы',
        model: 'FSP',
        manufacturer: 'Различные',
        quantity: 8,
        description: 'Удаление влаги, пыли, механических примесей. Пропускная способность: 736.94 NKm³/час'
      },
      {
        name: 'Ультразвуковой расходомер',
        model: 'DANIEL 3400',
        manufacturer: 'Daniel (США)',
        quantity: 9,
        description: 'Измерение принимаемого газа. Диапазон: 4487 - 1000000 нм³/час'
      },
      {
        name: 'Аппараты воздушного охлаждения',
        model: 'АВО-газа',
        manufacturer: 'Различные',
        quantity: 44,
        power: '37 кВт каждый',
        description: 'Охлаждение газа после компримирования. 22 линии, 44 кулера'
      }
    ],
    
    // Технические характеристики
    specifications: [
      {
        category: 'Проектная мощность',
        value: '30',
        unit: 'млрд м³/год',
        description: 'Максимальная годовая производительность станции'
      },
      {
        category: 'Количество ГПА',
        value: '5',
        unit: 'агрегатов',
        description: '2 Solar (15 МВт) + 3 GE (30 МВт)'
      },
      {
        category: 'Мощность Solar ГПА',
        value: '15',
        unit: 'МВт',
        description: 'Каждый из 2 агрегатов TITAN130'
      },
      {
        category: 'Мощность GE ГПА',
        value: '30',
        unit: 'МВт',
        description: 'Каждый из 3 агрегатов PGT25+'
      },
      {
        category: 'Диаметр трубопровода',
        value: '1067',
        unit: 'мм',
        description: 'Вход и выход, две параллельные нитки (А, В)'
      },
      {
        category: 'Давление входного газа',
        value: '7.0',
        unit: 'МПа',
        description: 'Проектное давление входного газопровода'
      },
      {
        category: 'Давление выходного газа',
        value: '9.81',
        unit: 'МПа',
        description: 'Проектное давление выходного газопровода'
      },
      {
        category: 'Расстояние от границы',
        value: '10.6',
        unit: 'км',
        description: 'От границы с Туркменистаном'
      },
      {
        category: 'Линии очистки газа',
        value: '8',
        unit: 'линий',
        description: '5 линий для нитки А, 3 линии для нитки В'
      },
      {
        category: 'Аппараты воздушного охлаждения',
        value: '22',
        unit: 'линий',
        description: '44 вентилятора для охлаждения газа'
      },
      {
        category: 'Линии узла замера газа',
        value: '9',
        unit: 'линий',
        description: '5 линий для нитки А, 4 линии для нитки В'
      },
      {
        category: 'Минимальный расход счетчика',
        value: '4487',
        unit: 'нм³/час',
        description: 'Минимальный диапазон измерений'
      },
      {
        category: 'Максимальный расход счетчика',
        value: '1000000',
        unit: 'нм³/час',
        description: 'Максимальный диапазон измерений'
      },
      {
        category: 'Газогенераторы',
        value: '3',
        unit: 'штук',
        description: 'Jenbacher JGS420 по 1451 кВт/час'
      },
      {
        category: 'Дизель-генератор',
        value: '260',
        unit: 'кВт/час',
        description: 'Volvo Penta для аварийного питания'
      },
      {
        category: 'Компрессоры сжатого воздуха',
        value: '2',
        unit: 'штук',
        description: 'Atlas Copco GA 132, производительность 1242 м³/ч'
      },
      {
        category: 'Циклонные сепараторы',
        value: '8',
        unit: 'штук',
        description: 'Пропускная способность 798.35 NKm³/час'
      },
      {
        category: 'Фильтры сепараторы',
        value: '8',
        unit: 'штук',
        description: 'Пропускная способность 736.94 NKm³/час'
      }
    ],
    
    // Системы безопасности и контроля
    safetySystems: [
      {
        name: 'Автоматическая система управления и регулирования',
        description: 'Управление всеми технологическими процессами каждого ГПА в автоматическом режиме',
        manufacturer: 'Siemens/GE',
        features: ['PID-регуляторы', 'Каскадное управление', 'Оптимизация режимов']
      },
      {
        name: 'Антипомпажное регулирование',
        description: 'Защита центробежных компрессоров от помпажа',
        manufacturer: 'GE/Solar',
        features: ['Датчики давления', 'Перепускные клапаны', 'Алгоритмы защиты']
      },
      {
        name: 'Система маслоснабжения',
        description: 'Обеспечивает подачу масла к подшипникам и уплотнениям ГПА',
        manufacturer: 'Различные',
        features: ['Масляные насосы', 'Фильтрация', 'Охлаждение масла']
      },
      {
        name: 'Система охлаждения',
        description: 'Воздушные теплообменники для охлаждения газа после компримирования',
        manufacturer: 'Различные',
        features: ['Воздушные теплообменники', 'Вентиляторы', 'Автоматическое регулирование']
      },
      {
        name: 'Система электроснабжения',
        description: 'Собственная генерация электроэнергии',
        manufacturer: 'GE/Volvo',
        features: ['Параллельная работа', 'АВР', 'Синхронизация']
      },
      {
        name: 'Слежение за уровнем вибрации',
        description: 'Непрерывный контроль уровня вибрации турбин и роторов компрессоров',
        manufacturer: 'Bently Nevada',
        features: ['Датчики вибрации', 'Анализ спектра', 'Аварийные сигналы']
      },
      {
        name: 'Контроль загазованности',
        description: 'Датчики концентрации метана и других газов во всех помещениях',
        manufacturer: 'Dräger',
        features: ['Датчики метана', 'Датчики CO', 'Датчики H₂S']
      },
      {
        name: 'Система пожарообнаружения',
        description: 'Автоматическое обнаружение очагов возгорания',
        manufacturer: 'Tyco/Honeywell',
        features: ['Тепловые датчики', 'Дымовые датчики', 'Датчики пламени']
      },
      {
        name: 'Автоматическое пожаротушение',
        description: 'Система газового и порошкового пожаротушения',
        manufacturer: 'Tyco',
        features: ['Газовое тушение FM-200', 'Порошковое тушение', 'Автоматический пуск']
      },
      {
        name: 'Система обогрева',
        description: 'Поддержание необходимой температуры в помещениях ГПА',
        manufacturer: 'Различные',
        features: ['Водяное отопление', 'Воздушные завесы', 'Терморегуляторы']
      },
      {
        name: 'Система вентиляции',
        description: 'Приточно-вытяжная вентиляция для обеспечения нормального воздухообмена',
        manufacturer: 'Различные',
        features: ['Приточные установки', 'Вытяжные вентиляторы', 'Фильтрация воздуха']
      },
      {
        name: 'Система пневмопитания',
        description: 'Обеспечивает сжатым воздухом пневматические приводы запорной арматуры',
        manufacturer: 'Atlas Copco',
        features: ['Воздушные компрессоры', 'Осушители воздуха', 'Ресиверы']
      }
    ],
    
    // Нормативные документы
    normativeDocs: [],
    
    // Фотографии станции
    photos: [
      { title: 'Общий вид станции', view: 'general' },
      { title: 'Машинный зал', view: 'machine-hall' },
      { title: 'Газоперекачивающие агрегаты', view: 'compressors' },
      { title: 'Система охлаждения', view: 'cooling' }
    ]
  },

  // Остальные станции остаются без изменений
  2: {
    id: 2,
    name: 'Компрессорная станция WKC2',
    shortName: 'WKC2',
    description: 'Компрессорная станция в системе газопровода ТУКК',
    image: 'WKC2.jpg',
    techMapImage: '/tex_kart/КС2 - WKC2_page-0001.jpg',
    power: '25 МВт',
    commissionDate: '2010',
    coursesCount: 6,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Компрессорная станция',
    designCapacity: '25 млрд м³/год',
    gasPressure: '7.5 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  },

  3: {
    id: 3,
    name: 'Компрессорная станция WKC3',
    shortName: 'WKC3',
    description: 'Компрессорная станция в системе газопровода ТУКК',
    image: 'WKC3.jpg',
    techMapImage: '/tex_kart/КС3 - WKC3_page-0001.jpg',
    power: '25 МВт',
    commissionDate: '2011',
    coursesCount: 7,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Компрессорная станция',
    designCapacity: '25 млрд м³/год',
    gasPressure: '7.5 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  },

  4: {
    id: 4,
    name: 'Участковая компрессорная станция UCS1',
    shortName: 'UCS1',
    description: 'Участковая компрессорная станция',
    image: 'UCS1.jpg',
    techMapImage: '/tex_kart/UCS1_page-0001.jpg',
    power: '15 МВт',
    commissionDate: '2012',
    coursesCount: 5,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Участковая компрессорная станция',
    designCapacity: '15 млрд м³/год',
    gasPressure: '6.0 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  },

  5: {
    id: 5,
    name: 'Участковая компрессорная станция UCS3',
    shortName: 'UCS3',
    description: 'Участковая компрессорная станция',
    image: 'UCS3.jpg',
    techMapImage: '/tex_kart/UCS3_page-0001.jpg',
    power: '15 МВт',
    commissionDate: '2013',
    coursesCount: 5,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Участковая компрессорная станция',
    designCapacity: '15 млрд м³/год',
    gasPressure: '6.0 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  },

  6: {
    id: 6,
    name: 'Газокомпрессорная станция GCS',
    shortName: 'GCS',
    description: 'Газокомпрессорная станция',
    image: 'GCS.jpg',
    techMapImage: '/tex_kart/GCS_page-0001.jpg',
    power: '20 МВт',
    commissionDate: '2014',
    coursesCount: 6,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Газокомпрессорная станция',
    designCapacity: '20 млрд м³/год',
    gasPressure: '6.5 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  },

  7: {
    id: 7,
    name: 'Магистральная станция MS',
    shortName: 'MS',
    description: 'Магистральная станция',
    image: 'MS.jpg',
    techMapImage: '/tex_kart/MS_page-0001.jpg',
    power: '18 МВт',
    commissionDate: '2015',
    coursesCount: 4,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Магистральная станция',
    designCapacity: '18 млрд м³/год',
    gasPressure: '6.0 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  },

  8: {
    id: 8,
    name: 'Участковая компрессорная станция UKMS',
    shortName: 'UKMS',
    description: 'Участковая компрессорная станция',
    image: 'UKMS.jpg',
    techMapImage: '/tex_kart/UKMS_page-0001.jpg',
    power: '12 МВт',
    commissionDate: '2016',
    coursesCount: 3,
    status: 'active',
    location: 'Республика Узбекистан',
    type: 'Участковая компрессорная станция',
    designCapacity: '12 млрд м³/год',
    gasPressure: '5.5 МПа',
    equipment: [],
    specifications: [],
    safetySystems: [],
    normativeDocs: [],
    photos: []
  }
}