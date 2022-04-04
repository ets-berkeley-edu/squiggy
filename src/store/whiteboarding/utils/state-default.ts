export default {
  // Variable that will keep track of the copied element(s)
  clipboard: [],
  debugLog: '',
  disableAll: true,
  downloadId: undefined,
  exportPngUrl: undefined,
  fitToScreen: true,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
  isExportingAsPng: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  isScrollingCanvas: false,
  mode: 'move',
  selected: {},
  sidebarExpanded: false,
  // Variable that will keep track of the point at which drawing a shape started
  startShapePointer: null,
  viewport: undefined,
  whiteboard: undefined
} as const
