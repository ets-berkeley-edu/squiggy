import _ from 'lodash'
import FABRIC_MULTIPLE_SELECT_TYPE from '@/store/whiteboarding/utils/constants'
import fabricator from '@/store/whiteboarding/utils/fabricator'
import utils from '@/api/api-utils'
import Vue from 'vue'
import {io} from 'socket.io-client'
import {fabric} from 'fabric'

const p = Vue.prototype

const init = (state: any, whiteboard: any) => {
  const socket = io(utils.apiBaseUrl(), {
    query: {
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
  Vue.prototype.$socket = socket
  $_addSocketListeners(state)
}

export default {
  init
}

const $_addSocketListeners = (state: any) => {
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
     p.$socket.on('add_whiteboard_elements', function(elements) {
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

/**
 * CONCURRENT EDITING
 * Deactivate the active group if any of the provided elements are a part of the active group
 * elements: The elements that should be checked for presence in the active group
 */
 const $_deactiveActiveGroupIfOverlap = (elements: any[]) => {
  const selection = p.$canvas.getActiveObject()
  if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
    const intersection = _.intersection(_.map(selection.objects, 'uuid'), _.map(elements, 'uuid'))
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
