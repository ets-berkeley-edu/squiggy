import _ from 'lodash'
import FABRIC_MULTIPLE_SELECT_TYPE from '@/store/whiteboarding/utils/constants'
import fabricator from '@/store/whiteboarding/utils/fabricator'
import socket from '@/store/whiteboarding/utils/socket'
import store from '@/store'
import Vue from 'vue'
import {fabric} from 'fabric'

const p = Vue.prototype

export function initialize(state: any, whiteboard: any) {
  $_initCanvas(state)
  $_addModalListeners()
  $_addViewportListeners(state)
  if (!whiteboard.deletedAt) {
    // Open a websocket connection for real-time communication with the server (chat + whiteboard changes) when
    // the whiteboard is rendered in edit mode. The course ID and API domain are passed in as handshake query parameters
    socket.init(state, whiteboard)
  }
  // The whiteboard p.$canvas should be initialized only after our additions are made to Fabric prototypes.
  fabricator.init(state)
}

const $_initCanvas = (state: any) => {
  // Initialize the Fabric.js canvas and load the whiteboard content and online users
  // Ensure that the horizontal and vertical origins of objects are set to center
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set the selection style for the whiteboard
  // Set the style of the multi-select helper
  Vue.prototype.$canvas = fabricator.createCanvas({
    selectionColor: 'transparent',
    selectionBorderColor: '#0295DE',
    selectionLineWidth: 2
  })
  // Make the border dashed
  // @see http://fabricjs.com/fabric-intro-part-4/
  p.$canvas.selectionDashArray = [10, 5]

  // Set the selection style for all elements
  fabric.Object.prototype.borderColor = '#0295DE'
  fabric.Object.prototype.borderScaleFactor = 0.3
  fabric.Object.prototype.cornerColor = '#0295DE'
  fabric.Object.prototype.cornerSize = 10
  fabric.Object.prototype.transparentCorners = false
  fabric.Object.prototype.rotatingPointOffset = 30
  // Set the pencil brush as the drawing brush
  p.$canvas.freeDrawingBrush = new fabric.PencilBrush(p.$canvas)
  // Render the whiteboard
  $_addListenters(state)
  $_renderWhiteboard(state)
}

const $_addListenters = (state: any) => {
  // Indicate that the currently selected elements are in the process of being moved, scaled or rotated
  const setModifyingElement = () => store.dispatch('whiteboarding/setIsModifyingElement', true)
  p.$canvas.on('object:moving', setModifyingElement)
  p.$canvas.on('object:scaling', setModifyingElement)
  p.$canvas.on('object:rotating', setModifyingElement)
  p.$canvas.on('object:moving', (event: any) => fabricator.ensureWithinCanvas(event))

  // One or multiple whiteboard canvas elements have been updated by the current user
  p.$canvas.on('object:modified', (event: any) => {
    // Ensure that none of the modified objects are positioned off screen
    fabricator.ensureWithinCanvas(event)
    // Get the selected whiteboard elements
    const elements = fabricator.getActiveElements()
    // Notify the server about the updates
    fabricator.saveElementUpdates(elements, state)
  })

  // Indicate that the currently selected elements are no longer being modified once moving, scaling or rotating has finished
  p.$canvas.on('object:modified', () => store.dispatch('whiteboarding/setIsModifyingElement', false))

  /**
   * Draw a box around the currently selected element(s) and use this box
   * to position the buttons that allow the selected element(s) to be modified
   */
  p.$canvas.on('after:render', () => store.dispatch('whiteboarding/afterCanvasRender'))

  /**
   * When a new group has been added programmatically added, it needs to be programmatically
   * removed from the canvas when the group is deselected
   */
  p.$canvas.on('before:selection:cleared', () => {
    const selection = p.$canvas.getActiveObject()
    if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(selection)
    }
  })

  // Recalculate the size of the whiteboard canvas when a selection has been deselected
  p.$canvas.on('selection:cleared', () => fabricator.setCanvasDimensions(state))

  /**
   * A new element was added to the whiteboard canvas by the current user
   */
  p.$canvas.on('object:added', (event: any) => {
    const element = event.target
    // Don't add a new text element until text has been entered
    if (element.type !== 'i-text' || element.text.trim()) {
      // If the element already has a unique id, it was added by a different user and there is no need to persist the addition
      if (!element.get('uuid') && !element.get('isHelper')) {
        fabricator.saveNewElement(element, state)
        // Recalculate the size of the whiteboard canvas
        fabricator.setCanvasDimensions(state)
      }
    }
  })

  /**
   * The mouse is pressed down on the whiteboard canvas
   */
   p.$canvas.on('mouse:down', (event: any) => {
    // Only start drawing a shape when the canvas is in shape mode
    if (state.mode === 'shape') {
      // Indicate that drawing a shape has started
      state.isDrawingShape = true

      // Keep track of the point where drawing the shape started
      state.startShapePointer = p.$canvas.getPointer(event.e)

      // Create the basic shape of the selected type that will
      // be used as the drawing guide. The originX and originY
      // of the helper element are set to left and top to make it
      // easier to map the top left corner of the drawing guide with
      // the original cursor postion
      const selected = state.shapeOptions.selected
      const shapeType = selected.type.shape
      const fill = selected.type.style === 'fill' ? state.shapeOptions.selected.color.color : 'transparent'
      state.shape = fabricator.createShape(shapeType, {
        fill,
        height: 1,
        left: state.startShapePointer.x,
        originX: 'left',
        originY: 'top',
        radius: 1,
        stroke: state.shapeOptions.selected.color.color,
        strokeWidth: state.shapeOptions.selected.type.style === 'thick' ? 10 : 2,
        top: state.startShapePointer.y,
        width: 1
      })
      // Indicate that this element is a helper element that should
      // not be saved back to the server
      state.shape.set('isHelper', true)
      p.$canvas.add(state.shape)
    }
  })

  /**
   * The mouse is moved on the whiteboard canvas
   */
  p.$canvas.on('mouse:move', (event: any) => {
    // Only continue drawing the shape when the whiteboard canvas is in shape mode
    if (state.isDrawingShape) {
      // Get the current position of the mouse
      const currentShapePointer = p.$canvas.getPointer(event.e)

      // When the user has moved the cursor to the left of the original
      // starting point, move the left of the circle to that point so
      // negative shape drawing can be achieved
      if (state.startShapePointer.x > currentShapePointer.x) {
        state.shape.set({left: currentShapePointer.x})
      }
      // When the user has moved the cursor above the original starting
      // point, move the left of the circle to that point so negative
      // shape drawing can be achieved
      if (state.startShapePointer.y > currentShapePointer.y) {
        state.shape.set({top: currentShapePointer.y})
      }

      // Set the radius and width of the circle based on how much the cursor
      // has moved compared to the starting point
      if (state.shapeOptions.selected.type.shape === 'Circle') {
        state.shape.set({
          height: Math.abs(state.startShapePointer.x - currentShapePointer.x),
          radius: Math.abs(state.startShapePointer.x - currentShapePointer.x) / 2,
          width: Math.abs(state.startShapePointer.x - currentShapePointer.x)
        })
      // Set the width and height of the shape based on how much the cursor
      // has moved compared to the starting point
      } else {
        state.shape.set({
          height: Math.abs(state.startShapePointer.y - currentShapePointer.y),
          width: Math.abs(state.startShapePointer.x - currentShapePointer.x)
        })
      }
      p.$canvas.requestRenderAll()
    }
  })

  /**
   * The mouse is released on the whiteboard canvas
   */
  p.$canvas.on('mouse:up', () => {
    if (state.isDrawingShape) {
      // Indicate that shape drawing has stopped
      state.isDrawingShape = false
      // Switch the toolbar back to move mode
      state.mode = 'move'
      // Clone the drawn shape and add the clone to the canvas.
      // This is caused by a bug in Fabric where it initially uses
      // the size when drawing started to position the controls. Cloning
      // ensures that the controls are added in the correct position.
      // The origin of the element is also set to `center` to make it
      // inline with the other whiteboard elements
      const finalShape = fabric.util.object.clone(state.shape)
      finalShape.left += finalShape.width / 2
      finalShape.top += finalShape.height / 2
      finalShape.originX = finalShape.originY = 'center'
      // Indicate that this is no longer a drawing helper shape and can
      // therefore be saved back to the server
      finalShape.set('isHelper', false)

      p.$canvas.add(finalShape)
      p.$canvas.remove(state.shape)
      // Select the added shape
      p.$canvas.setActiveObject(finalShape)
    }
  })
  /**
   * Add an editable text field to the whiteboard canvas
   */
   p.$canvas.on('mouse:down', (event: any) => {
    if (state.mode === 'text') {
      // Add the text field to where the user clicked
      const textPointer = p.$canvas.getPointer(event.e)

      // Start off with an empty text field
      const text = fabricator.createIText({
        fill: state.text.selected.color.color,
        fontFamily: '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
        fontSize: state.text.selected.size,
        left: textPointer.x,
        text: 'TODO: user input here!',
        top: textPointer.y
      })
      p.$canvas.add(text)

      // Put the editable text field in edit mode straight away
      setTimeout(function() {
        p.$canvas.setActiveObject(text)
        text.enterEditing()
        // The textarea needs to be put in edit mode manually
        // @see https://github.com/kangax/fabric.js/issues/1740
        text.hiddenTextarea.focus()
      }, 0)
    }
  })
}

const $_renderWhiteboard = (state: any) => {
  // Render the whiteboard and its elements
  // Set the size of the whiteboard canvas once all layout changes
  // regarding the sidebar have been applied
  setTimeout(() => fabricator.setCanvasDimensions(state), 0)

  // Restore the order of the layers once all elements have finished loading
  const restore = _.after(state.whiteboard.whiteboardElements.length, () => {
    fabricator.restoreLayers(state)
    // Deactivate all elements and element selection when the whiteboard
    // is being rendered in read only mode
    if (state.whiteboard.deletedAt) {
      p.$canvas.discardActiveObject()
      p.$canvas.selection = false
    }
  })
  // Restore the layout of the whiteboard canvas
  _.each(state.whiteboard.whiteboardElements, (element: any) => {
    fabricator.deserializeElement(state, element.element, (e: any) => {
      p.$canvas.add(e)
      restore()
    })
  })
}

const $_addModalListeners = () => {
  // TODO: Set the toolbar back to move mode when the asset and export tooltips are hidden.
  // state.$on('tooltip.hide', function(ev, $tooltip) {
  //   if ((state.mode === 'asset' && $tooltip.$id === 'whiteboards-board-asset-trigger') || (state.mode === 'export' && $tooltip.$id === 'whiteboards-board-export-trigger')) {
  //     state.mode = 'move'
  //   }
  // })
  // // Change the drawing color when a new color has been selected in the color picker
  // state.$watch('draw.selected.color', () => p.$canvas.freeDrawingBrush.color = state.draw.selected.color.color, true)
  // // Change the drawing line width when a new line width has been selected in the width picker
  // state.$watch('draw.selected.lineWidth', () => p.$canvas.freeDrawingBrush.width = parseInt(state.draw.selected.lineWidth, 10), true)
}

/**
 * Detect keydown events in the whiteboard to respond to keyboard shortcuts
 */
const $_addViewportListeners = (state: any) => {
  state.viewport.addEventListener('keydown', (event: any) => {
    // Remove the selected elements when the delete or backspace key is pressed
    if (event.keyCode === 8 || event.keyCode === 46) {
      fabricator.deleteActiveElements(state)
      event.preventDefault()
    } else if (event.keyCode === 67 && event.metaKey) {
      // Copy the selected elements
      state.clipboard = fabricator.getActiveElements()
    } else if (event.keyCode === 86 && event.metaKey) {
      // listeners.Paste the copied elements
      fabricator.paste(state)
    }
  }, false)
}
