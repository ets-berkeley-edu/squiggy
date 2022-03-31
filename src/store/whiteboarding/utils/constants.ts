
const FABRIC_OBJECT_EVENTS = ['event:added', 'event:deselected', 'event:dragenter', 'event:dragleave', 'event:dragover', 'event:drop', 'event:modified', 'event:modified', 'event:mousedblclick', 'event:mousedown', 'event:mouseout', 'event:mouseover', 'event:mouseup', 'event:mousewheel', 'event:moved', 'event:moving', 'event:removed', 'event:rotated', 'event:rotating', 'event:scaled', 'event:scaling', 'event:selected', 'event:skewed', 'event:skewing']

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
  COLORS: [
    {
      name: 'Black',
      color: 'rgb(0, 0, 0)'
    },
    {
      name: 'Dark Blue',
      color: 'rgb(90, 108, 122)'
    },
    {
      name: 'Light Blue',
      color: 'rgb(2, 149, 222)'
    },
    {
      name: 'Green',
      color: 'rgb(10, 139, 0)'
    },
    {
      name: 'Grey',
      color: 'rgb(230, 230, 230)'
    },
    {
      name: 'Purple',
      color: 'rgb(188, 58, 167)'
    },
    {
      name: 'Red',
      color: 'rgb(175, 56, 55)'
    },
    {
      name: 'Yellow',
      color: 'rgb(189, 129, 0)'
    }
  ],
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
  TEXT_OPTIONS: [
    {
      value: 36,
      label: '<span class="whiteboards-text-option">Title</span>'
    },
    {
      value: 14,
      label: '<span class="whiteboards-text-option">Normal</span>'
    }
  ]
}
