import _ from 'lodash'
import fabricator from '@/store/whiteboarding/fabricator'
import Vue from 'vue'
import {fabric} from 'fabric'
import {io} from 'socket.io-client'

const p = Vue.prototype

/**
 * Depending on the size of the whiteboard, exporting it to PNG can sometimes take a while. To
 * prevent the user from clicking the button twice when waiting to get a response, the button
 * will be disabled as soon as its clicked. Once the file has been downloaded, it will be
 * re-enabled. However, there are no cross-browser events that expose whether a file has been
 * downloaded. The PNG export endpoint works around this by taking in a `downloadId` parameter
 * and using that to construct a predictable cookie name. When a user clicks the button, the UI
 * will disable the button and wait until the cookie is set before re-enabling it again
 */
export function createDownloadId() {
  return new Date().getTime()
}

export function initFabricCanvas(state: any) {
  // Initialize the Fabric.js canvas and load the whiteboard content and online users
  // Ensure that the horizontal and vertical origins of objects are set to center
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set the selection style for the whiteboard
  // Set the style of the multi-select helper
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

const initSocket = (whiteboard: any) => {
  // Open a websocket connection for real-time communication with the server (chat + whiteboard changes) when
  // the whiteboard is rendered in edit mode. The course ID and API domain are passed in as handshake query parameters
  if (whiteboard.deletedAt) {
    return undefined
  }
  const socket = io(window.location.origin, {
    'transports': ['websocket'],
    'query': {
      whiteboardId: whiteboard.id
    }
  })
  socket.on('connect', function() {
    console.log('Websocket connected')
  })
  socket.on('disconnect', function() {
    console.log('Websocket disconnected')
  })
  /**
   * When a user has joined or left the whiteboard, update the online status on the list of members
   */
  socket.on('online', function(onlineUsers) {
    if (whiteboard) {
      for (let i = 0; i < whiteboard.members.length; i++) {
        const member = whiteboard.members[i]
        member.online = _.find(onlineUsers, {'user_id': member.id}) ? true : false
      }
    }
  })
  return socket
}

export default {
  initFabricCanvas,
  initSocket
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
      p.$canvas.deactivateAll()
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
