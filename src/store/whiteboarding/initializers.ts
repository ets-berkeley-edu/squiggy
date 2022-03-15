import _ from 'lodash'
import fabric from 'fabric'
import fabricator from '@/store/whiteboarding/fabricator'
import {io} from 'socket.io-client'

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

export function initFabricCanvas(state: any) {
  // Initialize the Fabric.js state.canvas and load the whiteboard content and online users
  // Ensure that the horizontal and vertical origins of objects are set to center
  state.fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set the selection style for the whiteboard
  // Set the style of the multi-select helper
  state.canvas.selectionColor = 'transparent'
  state.canvas.selectionBorderColor = '#0295DE'
  state.canvas.selectionLineWidth = 2
  // Make the border dashed
  // @see http://fabricjs.com/fabric-intro-part-4/
  state.canvas.selectionDashArray = [10, 5]

  // Set the selection style for all elements
  state.fabric.Object.prototype.borderColor = '#0295DE'
  state.fabric.Object.prototype.borderScaleFactor = 0.3
  state.fabric.Object.prototype.cornerColor = '#0295DE'
  state.fabric.Object.prototype.cornerSize = 10
  state.fabric.Object.prototype.transparentCorners = false
  state.fabric.Object.prototype.rotatingPointOffset = 30
  // Set the pencil brush as the drawing brush
  state.canvas.freeDrawingBrush = new fabric.PencilBrush(state.canvas)
  // Render the whiteboard
  $_renderWhiteboard(state)
}

export default {
  initFabricCanvas,
  initSocket
}

const $_renderWhiteboard = (state: any) => {
  // Render the whiteboard and its elements
  // Set the size of the whiteboard state.canvas once all layout changes
  // regarding the sidebar have been applied
  setTimeout(() => fabricator.setCanvasDimensions(state), 0)

  // Restore the order of the layers once all elements have finished loading
  const restore = _.after(state.whiteboard.whiteboard_elements.length, function() {
    fabricator.restoreLayers(state)
    // Deactivate all elements and element selection when the whiteboard
    // is being rendered in read only mode
    if (state.whiteboard.deletedAt) {
      state.canvas.deactivateAll()
      state.canvas.selection = false
    }
  })
  // Restore the layout of the whiteboard state.canvas
  _.each(state.whiteboard.whiteboard_elements, (element: any) => {
    fabricator.deserializeElement(state, element, (e: any) => {
      state.canvas.add(e)
      restore()
    })
  })
}
