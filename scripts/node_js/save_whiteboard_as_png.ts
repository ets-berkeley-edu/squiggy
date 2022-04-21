import _ from 'lodash'
const fs = require('fs')
import {fabric} from 'fabric'

const BASE_DIR = '/var/app/current'
const WHITEBOARD_PADDING = 10

// Command-line args must include absolute path to whiteboard-elements JSON file.
let whiteboardElements = []

_.each(process.argv, (arg: any) => {
  if (_.endsWith(arg, 'whiteboardElements.json')) {
    whiteboardElements = require(arg)
    return false
  }
})

// Initialize fabric
fabric.nodeCanvas.registerFont(`${BASE_DIR}/public/fonts/HelveticaNeueuLight.ttf`, {
  family: 'HelveticaNeue-Light',
  weight: 'regular',
  style: 'normal'
})
// Horizontal and vertical origins are set to center
fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'

// Outer corners of elements in the canvas
let left = Number.MAX_VALUE
let top = Number.MAX_VALUE
let right = Number.MIN_VALUE
let bottom = Number.MIN_VALUE

const deserializedElements: any[] = []

_.each(whiteboardElements, function(whiteboardElement) {
  // Canvas doesn't seem to deal terribly well with text elements that specify a prioritized list
  // of font family names. It seems that the only way to render custom fonts is to only specify one
  console.log('>> whiteboardElement')
  if (whiteboardElement.fontFamily) {
    whiteboardElement.fontFamily = 'HelveticaNeue-Light'
  }
  // Deserialize the element, get its boundary and check how large the canvas should be to display the element entirely.
  const type = fabric.util.string.camelize(fabric.util.string.capitalize(whiteboardElement.type))
  fabric[type].fromObject(whiteboardElement, (deserializedElement: any) => {
    // When all elements have been added to the canvas, we will make sure each has its proper index.
    deserializedElements.push(deserializedElement)

    const bound = deserializedElement.getBoundingRect()
    left = Math.min(left, bound.left)
    top = Math.min(top, bound.top)
    right = Math.max(right, bound.left + bound.width)
    bottom = Math.max(bottom, bound.top + bound.height)

    render()
  })
})

const render = _.after(whiteboardElements.length, function() {
  // At this point we've figured out what the left-most and right-most element is. By subtracting
  // their X-coordinates we get the desired width of the canvas. The height can be calculated in
  // a similar way by using the Y-coordinates
  let width = right - left
  let height = bottom - top

  // Neither width nor height should exceed 2048px.
  let scaleFactor = 1
  if (width > 2048 && width >= height) {
    scaleFactor = 2048 / width
  } else if (height > 2048 && height > width) {
    scaleFactor = 2048 / height
  }
  if (scaleFactor < 1) {
    // If scaling down is required, first change the canvas dimensions.
    width = width * scaleFactor
    height = height * scaleFactor
    // Next, scale and reposition each element against top left corner of the canvas.
    _.each(deserializedElements, function(element) {
      element.scaleX = element.scaleX * scaleFactor
      element.scaleY = element.scaleY * scaleFactor
      element.left = left + ((element.left - left) * scaleFactor)
      element.top = top + ((element.top - top) * scaleFactor)
    })
  }
  // Add a bit of padding so elements don't stick to the side
  width += (2 * WHITEBOARD_PADDING)
  height += (2 * WHITEBOARD_PADDING)

  // Create a canvas and pan it to the top-left corner
  const canvas = new fabric.Canvas(null, {
    backgroundColor: '#fff',
    width: width,
    height: height,
  })

  const pt = new fabric.Point(left - WHITEBOARD_PADDING, top - WHITEBOARD_PADDING)
  canvas.absolutePan(pt)

  // Don't render each element when it's added, rather render the entire Canvas once all elements
  // have been added. This is significantly faster
  canvas.renderOnAddRemove = false

  // Once all elements have been added to the canvas, restore
  // the layer order and convert to PNG
  const finishRender = _.after(deserializedElements.length, function() {
    // Ensure each element is placed at the right index. This can only happen
    // once all elements have been added to the canvas
    canvas.getObjects().sort(function(elementA, elementB) {
      return elementA.index - elementB.index
    })

    // Render the canvas
    canvas.renderAll()
    // Convert the canvas to a PNG file and return the data
    canvas.createPNGStream().pipe(fs.createWriteStream(`${BASE_DIR}/whiteboard.png`))
    return
  })

  // Add each element to the canvas
  _.each(deserializedElements, function(deserializedElement) {
    canvas.add(deserializedElement)
    finishRender()
  })
})
