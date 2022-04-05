import _ from 'lodash'

const FABRIC_OBJECT_EVENTS = ['event:added', 'event:deselected', 'event:dragenter', 'event:dragleave', 'event:dragover', 'event:drop', 'event:modified', 'event:modified', 'event:mousedblclick', 'event:mousedown', 'event:mouseout', 'event:mouseover', 'event:mouseup', 'event:mousewheel', 'event:moved', 'event:moving', 'event:removed', 'event:rotated', 'event:rotating', 'event:scaled', 'event:scaling', 'event:selected', 'event:skewed', 'event:skewing']

const $_getFabricJsDebugEventsExclude = () => {
  const eventNames = process.env.VUE_APP_FABRIC_JS_DEBUG_EVENTS_EXCLUDE
  return eventNames === '*' ? eventNames : _.split(eventNames, ',')
}

export default {
  // Variable that will keep track of the placeholder images to use for assets without a preview image
  ASSET_PLACEHOLDERS: {
    file: '/assets/img/whiteboard_asset_placeholder_file.png',
    link: '/assets/img/whiteboard_asset_placeholder_link.png',
    whiteboard: '/assets/img/whiteboard_asset_placeholder_whiteboard.png'
  },
  // The base width of the canvas
  CANVAS_BASE_WIDTH: 1000,
  // The padding that will be enforced on the canvas when it can be scrolled
  CANVAS_PADDING: 60,
  COLORS: {
    black: {
      hex: '#000000',
      rgb: 'rgb(0, 0, 0)'
    },
    darkBlue: {
      hex: '#5a6c7a',
      rgb: 'rgb(90, 108, 122)'
    },
    lightBlue: {
      hex: '#0295de',
      rgb: 'rgb(2, 149, 222)'
    },
    green: {
      hex: '#0a8b00',
      rgb: 'rgb(10, 139, 0)'
    },
    grey: {
      hex: '#e6e6e6',
      rgb: 'rgb(230, 230, 230)'
    },
    purple: {
      hex: '#bc3aa7',
      rgb: 'rgb(188, 58, 167)'
    },
    red: {
      hex: '#af3837',
      rgb: 'rgb(175, 56, 55)'
    },
    yellow: {
      hex: '#bd8100',
      rgb: 'rgb(189, 129, 0)'
    }
  },
  DRAW_OPTIONS: [
    {
      value: 1,
      label: '<img src="/assets/img/whiteboard-draw-small.png" />'
    },
    {
      value: 5,
      label: '<img src="/assets/img/whiteboard-draw-medium.png" />'
    },
    {
      value: 10,
      label: '<img src="/assets/img/whiteboard-draw-large.png" />'
    }
  ],
  FABRIC_EVENTS_PER_TYPE: {
    Canvas: FABRIC_OBJECT_EVENTS.concat(['after:render', 'before:render', 'before:selection:cleared', 'before:transform', 'canvas:cleared', 'drop:before', 'mouse:dblclick', 'mouse:down:before', 'mouse:down', 'mouse:move:before', 'mouse:move', 'mouse:out', 'mouse:over', 'mouse:up:before', 'mouse:up', 'object:added', 'object:modified', 'object:moving', 'object:removed', 'object:rotating', 'object:scaling', 'object:skewing', 'path:created', 'selection:cleared', 'selection:created', 'selection:updated']),
    IText: FABRIC_OBJECT_EVENTS.concat(['event:changed', 'selection:changed', 'editing:entered', 'editing:exited']),
    Object: FABRIC_OBJECT_EVENTS
  },
  FABRIC_JS_DEBUG_EVENTS_EXCLUDE: $_getFabricJsDebugEventsExclude(),
  FABRIC_MULTIPLE_SELECT_TYPE: 'activeSelection',
  MODE_OPTIONS: ['move', 'draw', 'shape', 'text', 'asset'],
  SHAPE_OPTIONS: [
    {
      shape: 'Rect',
      style: 'thin',
      label: '<img src="/assets/img/whiteboard-shape-rect-thin.png" />'
    },
    {
      shape: 'Rect',
      style: 'thick',
      label: '<img src="/assets/img/whiteboard-shape-rect-thick.png" />'
    },
    {
      shape: 'Rect',
      style: 'fill',
      label: '<img src="/assets/img/whiteboard-shape-rect-fill.png" />'
    },
    {
      shape: 'Circle',
      style: 'thin',
      label: '<img src="/assets/img/whiteboard-shape-circle-thin.png" />'
    },
    {
      shape: 'Circle',
      style: 'thick',
      label: '<img src="/assets/img/whiteboard-shape-circle-thick.png" />'
    },
    {
      shape: 'Circle',
      style: 'fill',
      label: '<img src="/assets/img/whiteboard-shape-circle-fill.png" />'
    }
  ],
  TEXT_SIZE_OPTIONS: [
    {text: 'Normal', value: 14},
    {text: 'Title', value: 36}
  ]
}
