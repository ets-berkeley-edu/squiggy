import _ from 'lodash'
import fabric from 'fabric'
import fabricator from '@/store/whiteboarding/fabricator'

const addFabricCanvasListenters = (state: any) => {
  // Indicate that the currently selected elements are in the process of being moved, scaled or rotated
  const setModifyingElement = () => state.isModifyingElement = true
  state.canvas.on('object:moving', setModifyingElement)
  state.canvas.on('object:scaling', setModifyingElement)
  state.canvas.on('object:rotating', setModifyingElement)
  state.canvas.on('object:moving', (event: any) => fabricator.ensureWithinCanvas(event, state))

  // One or multiple whiteboard state.canvas elements have been updated by the current user
  state.canvas.on('object:modified', (event: any) => {
    // Ensure that none of the modified objects are positioned off screen
    fabricator.ensureWithinCanvas(event, state)
    // Get the selected whiteboard elements
    const elements = fabricator.getActiveElements(state.canvas)
    // Notify the server about the updates
    fabricator.saveElementUpdates(elements, state)
  })

  // Indicate that the currently selected elements are no longer being modified once moving, scaling or rotating has finished
  state.canvas.on('object:modified', () => state.isModifyingElement = false)

  /**
   * Draw a box around the currently selected element(s) and use this box
   * to position the buttons that allow the selected element(s) to be modified
   */
  state.canvas.on('after:render', () => {
    if (!state.isModifyingElement && state.canvas.getActiveObject() || state.canvas.getActiveGroup()) {
      // Get the bounding rectangle around the currently selected element(s)
      let bound: any
      if (state.canvas.getActiveObject()) {
        bound = state.canvas.getActiveObject().getBoundingRect()
      } else if (state.canvas.getActiveGroup()) {
        bound = state.canvas.getActiveGroup().getBoundingRect()
      }
      if (bound) {
        // Explicitly draw the bounding rectangle
        state.canvas.contextContainer.strokeStyle = '#0295DE'
        state.canvas.contextContainer.strokeRect(bound.left - 10, bound.top - 10, bound.width + 20, bound.height + 20)
      }

      // Position the buttons to modify the selected element(s)
      const editButtons = document.getElementById('whiteboards-board-editelement')
      if (editButtons) {
        editButtons.style.left = (bound.left - 10) + 'px'
        editButtons.style.top = (bound.top + bound.height + 15) + 'px'
      }
    }
  })

  /**
   * When a new group has been added programmatically added, it needs to be programmatically
   * removed from the state.canvas when the group is deselected
   */
  state.canvas.on('before:selection:cleared', () => {
    if (state.canvas.getActiveGroup()) {
      state.canvas.remove(state.canvas.getActiveGroup())
    }
  })

  // Recalculate the size of the whiteboard state.canvas when a selection has been deselected
  state.canvas.on('selection:cleared', () => fabricator.setCanvasDimensions(state))

  /**
   * A new element was added to the whiteboard state.canvas by the current user
   */
  state.canvas.on('object:added', (event: any) => {
    const element = event.target
    // Don't add a new text element until text has been entered
    if (element.type === 'i-text' && !element.text.trim()) {
      return false
    }
    // If the element already has a unique id, it was added by a different user and
    // there is no need to persist the addition
    if (!element.get('uuid') && !element.get('isHelper')) {
      fabricator.saveNewElement(element, state)
      // Recalculate the size of the whiteboard state.canvas
      fabricator.setCanvasDimensions(state)
    }
  })

  /**
   * The mouse is pressed down on the whiteboard state.canvas
   */
   state.canvas.on('mouse:down', (event: any) => {
    // Only start drawing a shape when the state.canvas is in shape mode
    if (state.mode === 'shape') {
      // Indicate that drawing a shape has started
      state.isDrawingShape = true

      // Keep track of the point where drawing the shape started
      state.startShapePointer = state.canvas.getPointer(event.e)

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
      state.canvas.add(state.shape)
    }
  })

  /**
   * The mouse is moved on the whiteboard state.canvas
   */
  state.canvas.on('mouse:move', (event: any) => {
    // Only continue drawing the shape when the whiteboard state.canvas is in shape mode
    if (state.isDrawingShape) {
      // Get the current position of the mouse
      const currentShapePointer = state.canvas.getPointer(event.e)

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
      state.canvas.renderAll()
    }
  })

  /**
   * The mouse is released on the whiteboard state.canvas
   */
  state.canvas.on('mouse:up', () => {
    if (state.isDrawingShape) {
      // Indicate that shape drawing has stopped
      state.isDrawingShape = false
      // Switch the toolbar back to move mode
      state.mode = 'move'
      // Clone the drawn shape and add the clone to the state.canvas.
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

      state.canvas.add(finalShape)
      state.canvas.remove(state.shape)
      // Select the added shape
      state.canvas.setActiveObject(finalShape)
    }
  })
  /**
   * Add an editable text field to the whiteboard state.canvas
   */
   state.canvas.on('mouse:down', function(ev) {
    if (state.mode === 'text') {
      // Add the text field to where the user clicked
      const textPointer = state.canvas.getPointer(ev.e)

      // Start off with an empty text field
      const text = new fabric.IText('', {
        'left': textPointer.x,
        'top': textPointer.y,
        'fontFamily': '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
        'fontSize': state.text.selected.size,
        'fill': state.text.selected.color.color
      })
      state.canvas.add(text)

      // Put the editable text field in edit mode straight away
      setTimeout(function() {
        state.canvas.setActiveObject(text)
        text.enterEditing()
        // The textarea needs to be put in edit mode manually
        // @see https://github.com/kangax/fabric.js/issues/1740
        text.hiddenTextarea.focus()
      }, 0)
    }
  })
}

const addSocketListeners = (state: any) => {
  if (state.socket) {
    /**
     * One or multiple whiteboard state.canvas elements were updated by a different user
     */
    state.socket.on('updateActivity', (elements: any) => {
      // Deactivate the current group if any of the updated elements are in the current group
      $_deactiveActiveGroupIfOverlap(elements, state)
      // Update the elements
      _.each(elements, function(element) {
        $_updateCanvasElement(state, element.uuid, element)
      })
      // Recalculate the size of the whiteboard state.canvas
      fabricator.setCanvasDimensions(state)
    })
    /**
     * A whiteboard state.canvas element was added by a different user
     */
     state.socket.on('addActivity', function(elements) {
      _.each(elements, (element: any) => {
        const callback = (e: any) => {
          // Add the element to the whiteboard state.canvas and move it to its appropriate index
          state.canvas.add(e)
          element.moveTo(e.get('index'))
          state.canvas.renderAll()
          // Recalculate the size of the whiteboard state.canvas
          fabricator.setCanvasDimensions(state)
        }
        fabricator.deserializeElement(state, element, callback)
      })
    })

    /**
     * One or multiple whiteboard state.canvas elements were deleted by a different user
     */
    state.socket.on('deleteActivity', function(elements) {
      // Deactivate the current group if any of the deleted elements are in the current group
      $_deactiveActiveGroupIfOverlap(elements, state)
      // Delete the elements
      _.each(elements, function(element) {
        element = fabricator.getCanvasElement(state.canvas, element.uuid)
        if (element) {
          state.canvas.remove(element)
        }
      })
      // Recalculate the size of the whiteboard state.canvas
      fabricator.setCanvasDimensions(state)
    })
  }
}

const addModalListeners = (state: any) => {
  // Set the toolbar back to move mode when the asset and export tooltips are hidden.
  state.$on('tooltip.hide', function(ev, $tooltip) {
    if ((state.mode === 'asset' && $tooltip.$id === 'whiteboards-board-asset-trigger') || (state.mode === 'export' && $tooltip.$id === 'whiteboards-board-export-trigger')) {
      state.mode = 'move'
    }
  })
  // Change the drawing color when a new color has been selected in the color picker
  state.$watch('draw.selected.color', () => state.canvas.freeDrawingBrush.color = state.draw.selected.color.color, true)
  // Change the drawing line width when a new line width has been selected in the width picker
  state.$watch('draw.selected.lineWidth', () => state.canvas.freeDrawingBrush.width = parseInt(state.draw.selected.lineWidth, 10), true)
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
 const $_deactiveActiveGroupIfOverlap = (elements: any[], state: any) => {
  const group = state.canvas.getActiveGroup()
  if (group) {
    const intersection = _.intersection(_.map(group.objects, 'uuid'), _.map(elements, 'uuid'))
    if (intersection.length > 0) {
      state.canvas.discardActiveGroup().renderAll()
    }
  }
}

/**
 * Update the appearance of a Fabric.js state.canvas element
 *
 * @param  {Number}         uuid               The id of the element to update
 * @param  {Object}         update            The updated values to apply to the state.canvas element
 * @return {void}
 */
 const $_updateCanvasElement = (state: any, uuid: number, update: any): any => {
  const element = fabricator.getCanvasElement(state.canvas, uuid)

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
        state.canvas.renderAll()
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
