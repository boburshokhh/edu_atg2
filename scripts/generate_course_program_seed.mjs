import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import crypto from 'node:crypto'

// Resolve repo root
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..')

// Import stationsData (ESM)
const stationsDataUrl = pathToFileURL(path.join(repoRoot, 'src', 'data', 'stationsData.js')).href
const { stationsData } = await import(stationsDataUrl)

function normStr(s) {
  return String(s || '').trim()
}

function normalizeTopicTitle(s) {
  return normStr(s).toLowerCase().replace(/свм/g, 'cbm').replace(/cbm/g, 'cbm')
}

function findCourseMaterialsLesson(lessonTitle, courseMaterials) {
  const t1 = normStr(lessonTitle)
  const t2 = t1.replace(':', '.')
  return (courseMaterials.lessons || []).find(
    l => normStr(l.lessonTitle) === t1 || normStr(l.lessonTitle) === t2 || normStr(l.lessonTitle).replace(':', '.') === t2
  )
}

function findCourseMaterialsTopic(topic, lessonData) {
  const topicCodeFromData = normStr(topic.code).replace(/\.$/, '')
  const topicTitleFromData = normalizeTopicTitle(topic.title)

  return (lessonData.topics || []).find(t => {
    const topicCodeNormalized = normStr(t.topicCode).replace(/\.$/, '')
    const topicTitleNormalized = normalizeTopicTitle(t.topicTitle)
    const codeMatch = topicCodeNormalized === topicCodeFromData

    // allow minor title drift, but still require code match
    if (!codeMatch) return false
    if (!topicTitleNormalized || !topicTitleFromData) return true
    return topicTitleNormalized === topicTitleFromData
  })
}

// Load courseMaterials.json from disk (to allow writing back)
const courseMaterialsPath = path.join(repoRoot, 'src', 'data', 'courseMaterials.json')
const courseMaterials = JSON.parse(await readFile(courseMaterialsPath, 'utf-8'))

const seed = { stations: [] }

for (const [stationIdRaw, station] of Object.entries(stationsData || {})) {
  const stationId = Number(stationIdRaw)
  const cp = station?.courseProgram
  if (!cp) continue

  const program = {
    stationId,
    title: cp.title || '',
    description: cp.description || '',
    duration: cp.duration || '',
    format: cp.format || 'Онлайн',
    isActive: true,
    orderIndex: 0,
    learningOutcomes: Array.isArray(cp.learningOutcomes) ? cp.learningOutcomes : [],
    requirements: Array.isArray(cp.requirements) ? cp.requirements : [],
    targetAudience: Array.isArray(cp.targetAudience) ? cp.targetAudience : [],
    finalTest: cp.finalTest || null,
    lessons: [],
  }

  for (let lessonIndex = 0; lessonIndex < (cp.lessons || []).length; lessonIndex++) {
    const lesson = cp.lessons[lessonIndex]
    const lessonKey = `lesson_${crypto.randomUUID()}`
    const lessonOut = {
      lessonKey,
      title: lesson.title || '',
      duration: lesson.duration || '',
      orderIndex: lessonIndex,
      isActive: true,
      topics: [],
    }

    for (let topicIndex = 0; topicIndex < (lesson.topics || []).length; topicIndex++) {
      const topic = lesson.topics[topicIndex]
      const topicKey = `topic_${crypto.randomUUID()}`
      lessonOut.topics.push({
        topicKey,
        code: topic.code || '',
        title: topic.title || '',
        duration: topic.duration || '',
        orderIndex: topicIndex,
        isActive: true,
      })
    }

    program.lessons.push(lessonOut)
  }

  seed.stations.push({ stationId, program })

  // Update courseMaterials.json topicKey fields (best effort; mainly for station 1 data)
  // We match by lesson title + topic code/title.
  for (const lesson of program.lessons) {
    const lessonData = findCourseMaterialsLesson(lesson.title, courseMaterials)
    if (!lessonData) continue
    lessonData.lessonKey = lesson.lessonKey

    for (const topic of lesson.topics) {
      const topicData = findCourseMaterialsTopic(topic, lessonData)
      if (!topicData) continue
      topicData.topicKey = topic.topicKey
    }
  }
}

// Write seed file
const seedDir = path.join(repoRoot, 'backend_django', 'apps', 'courses', 'seed')
await mkdir(seedDir, { recursive: true })
const seedPath = path.join(seedDir, 'course_program_seed.json')
await writeFile(seedPath, JSON.stringify(seed, null, 2), 'utf-8')

// Write updated courseMaterials.json (adds topicKey/lessonKey)
await writeFile(courseMaterialsPath, JSON.stringify(courseMaterials, null, 2), 'utf-8')

console.log(`[generate_course_program_seed] Wrote seed: ${seedPath}`)
console.log(`[generate_course_program_seed] Updated course materials: ${courseMaterialsPath}`)
console.log(`[generate_course_program_seed] Stations with programs: ${seed.stations.length}`)


