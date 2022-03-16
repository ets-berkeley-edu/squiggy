import _ from 'lodash'
import fabricator from '@/store/whiteboarding/utils/fabricator'
import store from '@/store'
import Vue from 'vue'
import {fabric} from 'fabric'

const p = Vue.prototype

const addFabricCanvasListenters = (state: any) => {
  // Indicate that the currently selected elements are in the process of being moved, scaled or rotated
  const setModifyingElement = () => state.isModifyingElement = true
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
    if (p.$canvas.getActiveGroup()) {
      p.$canvas.remove(p.$canvas.getActiveGroup())
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
    if (element.type === 'i-text' && !element.text.trim()) {
      return false
    }
    // If the element already has a unique id, it was added by a different user and there is no need to persist the addition
    if (!element.get('uuid') && !element.get('isHelper')) {
      fabricator.saveNewElement(element)
      // Recalculate the size of the whiteboard canvas
      fabricator.setCanvasDimensions(state)
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
      state.shape = new fabric[state.shapeOptions.selected.type.shape]({
        'left': state.startShapePointer.x,
        'top': state.startShapePointer.y,
        'originX': 'left',
        'originY': 'top',
        'radius': 1,
        'width': 1,
        'height': 1,
        'fill': 'transparent',
        'stroke': state.shapeOptions.selected.color.color,
        'strokeWidth': state.shapeOptions.selected.type.style === 'thick' ? 10 : 2
      })
      if (state.shapeOptions.selected.type.style === 'fill') {
        state.shape.fill = state.shapeOptions.selected.color.color
      }
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
        state.shape.set({'left': currentShapePointer.x})
      }
      // When the user has moved the cursor above the original starting
      // point, move the left of the circle to that point so negative
      // shape drawing can be achieved
      if (state.startShapePointer.y > currentShapePointer.y) {
        state.shape.set({'top': currentShapePointer.y})
      }

      // Set the radius and width of the circle based on how much the cursor
      // has moved compared to the starting point
      if (state.shapeOptions.selected.type.shape === 'Circle') {
        state.shape.set({
          'width': Math.abs(state.startShapePointer.x - currentShapePointer.x),
          'height': Math.abs(state.startShapePointer.x - currentShapePointer.x),
          'radius': Math.abs(state.startShapePointer.x - currentShapePointer.x) / 2
        })
      // Set the width and height of the shape based on how much the cursor
      // has moved compared to the starting point
      } else {
        state.shape.set({
          'width': Math.abs(state.startShapePointer.x - currentShapePointer.x),
          'height': Math.abs(state.startShapePointer.y - currentShapePointer.y)
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
   p.$canvas.on('mouse:down', function(ev) {
    if (state.mode === 'text') {
      // Add the text field to where the user clicked
      const textPointer = p.$canvas.getPointer(ev.e)

      // Start off with an empty text field
      const text = new fabric.IText('', {
        'left': textPointer.x,
        'top': textPointer.y,
        'fontFamily': '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
        'fontSize': state.text.selected.size,
        'fill': state.text.selected.color.color
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

const addSocketListeners = (state: any) => {
  if (p.$socket) {
    /**
     * One or multiple whiteboard canvas elements were updated by a different user
     */
    p.$socket.on('updateActivity', (elements: any) => {
      // Deactivate the current group if any of the updated elements are in the current group
      $_deactiveActiveGroupIfOverlap(elements)
      // Update the elements
      _.each(elements, function(element) {
        $_updateCanvasElement(state, element.uuid, element)
      })
      // Recalculate the size of the whiteboard canvas
      fabricator.setCanvasDimensions(state)
    })
    /**
     * A whiteboard canvas element was added by a different user
     */
     p.$socket.on('addActivity', function(elements) {
      _.each(elements, (element: any) => {
        const callback = (e: any) => {
          // Add the element to the whiteboard canvas and move it to its appropriate index
          p.$canvas.add(e)
          element.moveTo(e.get('index'))
          p.$canvas.requestRenderAll()
          // Recalculate the size of the whiteboard canvas
          fabricator.setCanvasDimensions(state)
        }
        fabricator.deserializeElement(state, element, callback)
      })
    })

    /**
     * One or multiple whiteboard canvas elements were deleted by a different user
     */
    p.$socket.on('deleteActivity', function(elements) {
      // Deactivate the current group if any of the deleted elements are in the current group
      $_deactiveActiveGroupIfOverlap(elements)
      // Delete the elements
      _.each(elements, function(element) {
        element = fabricator.getCanvasElement(element.uuid)
        if (element) {
          p.$canvas.remove(element)
        }
      })
      // Recalculate the size of the whiteboard canvas
      fabricator.setCanvasDimensions(state)
    })
  }
}

const addModalListeners = () => {
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

export default {
  addModalListeners,
  addSocketListeners,
  addFabricCanvasListenters
}

/**
 * CONCURRENT EDITING
 * Deactivate the active group if any of the provided elements are a part of the active group
 * elements: The elements that should be checked for presence in the active group
 */
 const $_deactiveActiveGroupIfOverlap = (elements: any[]) => {
  const group = p.$canvas.getActiveGroup()
  if (group) {
    const intersection = _.intersection(_.map(group.objects, 'uuid'), _.map(elements, 'uuid'))
    if (intersection.length > 0) {
      p.$canvas.discardActiveGroup().requestRenderAll()
    }
  }
}

/**
 * Update the appearance of a Fabric.js canvas element
 *
 * @param  {Number}         uuid               The id of the element to update
 * @param  {Object}         update            The updated values to apply to the canvas element
 * @return {void}
 */
 const $_updateCanvasElement = (state: any, uuid: number, update: any): any => {
  const element = fabricator.getCanvasElement(uuid)

  const updateElementProperties = () => {
    // Update all element properties, except for the image source. The image
    // source is handled separately as this is an asynchronous action
    _.each(update, function(value, property) {
      if (property !== 'src' && value !== element.get(property)) {
        element.set(property, value)
      }
    })
    // When the source element for an asset has changed, update this last and
    // re-render the element after it has been loaded
    if (element.type === 'image' && element.getSrc() !== update.src) {
      element.setSrc(update.src, function() {
        p.$canvas.requestRenderAll()
        // Ensure that the correct position is applied
        fabricator.restoreLayers(state)
      })
    } else {
      fabricator.restoreLayers(state)
    }
  }
  // If the element is an asset for which the source has changed, we preload
  // the image to prevent flickering when the image is inserted into the element
  if (element.type === 'image' && element.getSrc() !== update.src) {
    fabric.util.loadImage(update.src, updateElementProperties)
  } else {
    updateElementProperties()
  }
}
