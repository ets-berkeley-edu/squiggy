import constants from '@/store/whiteboarding/utils/constants'
import {createDownloadId} from '@/store/whiteboarding/utils/canvas'

const defaultState = {
  // Variable that will keep track of the copied element(s)
  clipboard: [],
  colors: constants.COLORS,
  disableAll: true,
  downloadId: createDownloadId(),
  draw: {
    options: constants.DRAW_OPTIONS,
    selected: {
      lineWidth: constants.DRAW_OPTIONS[0].value,
      color: constants.COLORS[0]
    }
  },
  exportPngUrl: undefined,
  fabric: undefined,
  fitToScreen: true,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
  isExportingAsPng: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  mode: 'move',
  modeOptions: constants.MODE_OPTIONS,
  scrollingCanvas: false,
  // Variable that will keep track of the shape that is being added to the whiteboard canvas
  shape: null,
  // Variable that will keep track of the selected shape, style and draw color
  shapeOptions: {
    options: constants.SHAPE_OPTIONS,
    selected: {
      type: constants.SHAPE_OPTIONS[0],
      color: constants.COLORS[0]
    }
  },
  sidebarExpanded: false,
  sidebarMode: 'online',
  // Variable that will keep track of the point at which drawing a shape started
  startShapePointer: null,
  unsavedFabricElement: undefined, // TODO: remove?
  viewport: undefined,
  whiteboard: undefined,
  text: {
    'options': constants.TEXT_OPTIONS,
    'selected': {
      'size': constants.TEXT_OPTIONS[-1],
      'color': constants.COLORS[0]
    }
  }
} as const

export default defaultState
