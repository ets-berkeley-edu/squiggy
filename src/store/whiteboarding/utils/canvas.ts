import _ from 'lodash'
import fabricator from '@/store/whiteboarding/utils/fabricator'
import Vue from 'vue'
import {fabric} from 'fabric'

const p = Vue.prototype

export function init(state: any) {
  // Initialize the Fabric.js canvas and load the whiteboard content and online users
  // Ensure that the horizontal and vertical origins of objects are set to center
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set the selection style for the whiteboard
  // Set the style of the multi-select helper
  Vue.prototype.$canvas = new fabric.Canvas('canvas', {
    backgroundColor: 'red'
  })
  p.$canvas.selectionColor = 'transparent'
  p.$canvas.selectionBorderColor = '#0295DE'
  p.$canvas.selectionLineWidth = 2
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
  $_renderWhiteboard(state)
}

const $_renderWhiteboard = (state: any) => {
  // Render the whiteboard and its elements
  // Set the size of the whiteboard canvas once all layout changes
  // regarding the sidebar have been applied
  setTimeout(() => fabricator.setCanvasDimensions(state), 0)

  // Restore the order of the layers once all elements have finished loading
  const restore = _.after(state.whiteboard.whiteboardElements.length, function() {
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
    fabricator.deserializeElement(state, element, (e: any) => {
      p.$canvas.add(e)
      restore()
    })
  })
}

export default {
  init
}
