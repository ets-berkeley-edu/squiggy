import _ from 'lodash'
const fs = require('fs')
import {fabric} from 'fabric'

/**
 * NOTE: The steps below are automated for you in 'scripts/developer_debug_whiteboard_as_png.sh'.
 *
 * USAGE:
 *  1. Create mock data in elements.json (array of serialized fabric objects, as seen in Squiggy database).
 *  2. cd to Squiggy base directory
 *  3. Run command
 *      node \
 *        ./scripts/node_js/save_whiteboard_as_png.js
 *        -b /path/to/squiggy \
 *        -p "/path/to/output/whiteboard.png" \
 *        -v true \
 *        -w "/path/to/elements.json"
 */

const WHITEBOARD_PADDING = 10

// @ts-ignore
const args = process.argv
const getArg = (flag: string) => {
  const index = args.indexOf(flag)
  return (index > -1 && index < args.length - 1) ? args[index + 1] : null
}
const baseDir = getArg('-b')
const verbose = _.trim(getArg('-v'))
const pngFile = getArg('-p')
let elements = require(getArg('-w'))

if (!baseDir || !pngFile || !elements) {
  throw new Error('Required arg(s) are missing. baseDir=' + baseDir + '; pngFile=' + pngFile + '; elements=' + elements + ';')
}

elements = _.sortBy(elements, (e: any) => `${e.index}-${e.uuid}`)

// Initialize fabric
fabric.nodeCanvas.registerFont(`${baseDir}/dist/static/fonts/HelveticaNeueuLight.ttf`, {
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

let deserializedElements: any[] = []

$_log('Begin')

let countProcessed = 0

_.each(elements, (element: any) => {
  // Canvas doesn't seem to deal terribly well with text elements that specify a prioritized list
  // of font family names. It seems that the only way to render custom fonts is to only specify one
  if (element.fontFamily) {
    element.fontFamily = 'HelveticaNeue-Light'
  }
  // Deserialize the element, get its boundary and check how large the canvas should be to display the element entirely.
  const type = fabric.util.string.camelize(fabric.util.string.capitalize(element.type))
  $_createFabricObject(element, type).then((e: any) => {
    $_log(`${_.capitalize(e.type)} element deserialized (uuid: ${e.uuid})`, false)
    deserializedElements.push(e)
    const bound = e.getBoundingRect()
    // The values below determine canvas size during render.
    left = Math.min(left, bound.left)
    top = Math.min(top, bound.top)
    right = Math.max(right, bound.left + bound.width)
    bottom = Math.max(bottom, bound.top + bound.height)

    countProcessed++
    $_log(`Processed ${countProcessed} of ${elements.length}`)
    if (countProcessed === elements.length) {
      $_render()
    }
  })
})

function $_createFabricObject(element, type) {
  return new Promise<any>(resolve => {
    fabric[type].fromObject(element, (e: any) => {
      if (element.type === 'image') {
        e.setSrc(element.src, resolve)
      } else {
        resolve(e)
      }
    })
  })
}

function $_log(statement: string, force?: boolean) {
  if (verbose.toLowerCase() === 'true' || force) {
    console.log(`🪲 ${statement}`)
  }
}

function $_render() {
  $_log('Finally, render the Fabric.js canvas.')
  // At this point we've figured out what the left-most and right-most element is. By subtracting
  // their X-coordinates we get the desired width of the canvas. The height can be calculated in
  // a similar way by using the Y-coordinates
  let width = right - left
  let height = bottom - top
  // Neither width nor height should exceed 2048px.
  let scale_factor = 1
  if (width > 2048 && width >= height) {
    scale_factor = 2048 / width
  } else if (height > 2048 && height > width) {
    scale_factor = 2048 / height
  }
  if (scale_factor < 1) {
    // If scaling down is required, first change the canvas dimensions.
    width = width * scale_factor
    height = height * scale_factor
    // Next, scale and reposition each element against top left corner of the canvas.
    _.each(deserializedElements, (element) => {
      element.scaleX = element.scaleX * scale_factor
      element.scaleY = element.scaleY * scale_factor
      element.left = left + ((element.left - left) * scale_factor)
      element.top = top + ((element.top - top) * scale_factor)
    })
  }
  // Add a bit of padding so elements don't stick to the side
  width += (2 * WHITEBOARD_PADDING)
  height += (2 * WHITEBOARD_PADDING)

  // Create a canvas and pan it to the top-left corner
  const canvas = new fabric.Canvas(null, {backgroundColor: '#fff', width, height})
  canvas.absolutePan(new fabric.Point(left - WHITEBOARD_PADDING, top - WHITEBOARD_PADDING))

  // Render canvas AFTER all elements have been added. This is significantly faster
  canvas.renderOnAddRemove = false

  deserializedElements = _.sortBy(deserializedElements, (e: any) => `${e.index}-${e.uuid}`)

  // Add each element to the canvas
  _.each(deserializedElements, (deserializedElement: any, index: number) => {
    canvas.add(deserializedElement)
    if (index + 1 === deserializedElements.length) {
      canvas.renderAll()
      canvas.createPNGStream().pipe(fs.createWriteStream(pngFile))
      $_log('Done.')
    }
  })
}
