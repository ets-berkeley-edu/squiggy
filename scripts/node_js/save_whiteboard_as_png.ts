import _ from 'lodash'
const fs = require('fs')
import {fabric} from 'fabric'

const WHITEBOARD_PADDING = 10

/**
 * USAGE:
 * 1. IMPORTANT:
 *    (a) Changes to this Typescript file must be compiled with `scripts/compile_whiteboard_to_png.sh`
 *    (b) Use `scripts/developer_debug_whiteboard_as_png.sh` to test PNG generation without running Squiggy webapp.
 * 2. Create mock data in elements.json (array of serialized fabric objects, as seen in Squiggy database).
 * 3. cd to Squiggy base directory
 * 4. Run command
 *      node \
 *        ./scripts/node_js/save_whiteboard_as_png.js
 *        -b /path/to/squiggy \
 *        -p "/path/to/output/whiteboard.png"
 *        -v true
 *        -w "/path/to/elements.json" \
 * 5. [OPTIONAL] Put the node command above into a script named 'scripts/run_whiteboard_as_png_local.sh' (git-ignored)
 */

// @ts-ignore
const args = process.argv
const getArg = (flag: string) => {
  const index = args.indexOf(flag)
  return (index > -1 && index < args.length - 1) ? args[index + 1] : null
}
const baseDir = getArg('-b')
const verbose = getArg('-v')
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

_.each(elements, (element: any) => {
  // Canvas doesn't seem to deal terribly well with text elements that specify a prioritized list
  // of font family names. It seems that the only way to render custom fonts is to only specify one
  if (element.fontFamily) {
    element.fontFamily = 'HelveticaNeue-Light'
  }
  // Deserialize the element, get its boundary and check how large the canvas should be to display the element entirely.
  const type = fabric.util.string.camelize(fabric.util.string.capitalize(element.type))

  const $_after = _.after(elements.length, () => $_render())

  const $_push = (e: any) => {
    $_log(`${_.capitalize(e.type)} element deserialized (uuid: ${e.uuid})`, false)
    deserializedElements.push(e)
    const bound = e.getBoundingRect()
    // The values below determine canvas size during render.
    left = Math.min(left, bound.left)
    top = Math.min(top, bound.top)
    right = Math.max(right, bound.left + bound.width)
    bottom = Math.max(bottom, bound.top + bound.height)
    $_after()
  }
  if (element.type === 'image') {
    fabric[type].fromObject(element, (e: any) => {
      e.setSrc(element.src, (e: any) => $_push(e))
    })
  } else {
    fabric[type].fromObject(element, (e: any) => $_push(e))
  }
})

function $_log(statement: string, force?: boolean) {
  if (verbose.toLowerCase() === 'true' || force) {
    console.log(`🪲 ${statement}`)
  }
}

const $_render = () => {
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
    _.each(deserializedElements, function(element) {
      element.scaleX = element.scaleX * scale_factor
      element.scaleY = element.scaleY * scale_factor
      element.left = left + ((element.left - left) * scale_factor)
      element.top = top + ((element.top - top) * scale_factor)
    })
  }
  // Add a bit of padding so elements don't stick to the side
  width += (2 * WHITEBOARD_PADDING)
  height += (2 * WHITEBOARD_PADDING)

  $_log(`Begin render with:\n width=${width} \n height=${height} \n scale_factor=${scale_factor} \n width=${width} \n width=${width}`)

  // Create a canvas and pan it to the top-left corner
  const canvas = new fabric.Canvas(null, {backgroundColor: '#fff', width, height})
  canvas.absolutePan(new fabric.Point(left - WHITEBOARD_PADDING, top - WHITEBOARD_PADDING))

  // Render canvas AFTER all elements have been added. This is significantly faster
  canvas.renderOnAddRemove = false

  deserializedElements = _.sortBy(deserializedElements, (e: any) => `${e.index}-${e.uuid}`)

  // Add each element to the canvas
  const $_after = _.after(deserializedElements.length, () => {
    canvas.renderAll()
    canvas.createPNGStream().pipe(fs.createWriteStream(pngFile))
    $_log('Done.')
  })

  _.each(deserializedElements, (deserializedElement: any) => {
    canvas.add(deserializedElement)
    $_after()
  })
}
