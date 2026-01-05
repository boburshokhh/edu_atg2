import { inject, provide } from 'vue'

export const StationEditorKey = Symbol('StationEditor')

/**
 * Provide station editor context to child components
 */
export function provideStationEditorContext(context) {
  provide(StationEditorKey, context)
}

/**
 * Inject station editor context in child components
 */
export function useStationEditorContext() {
  const context = inject(StationEditorKey)
  if (!context) {
    throw new Error('useStationEditorContext must be used within StationEditor')
  }
  return context
}

