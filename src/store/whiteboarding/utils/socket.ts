import _ from 'lodash'
import utils from '@/api/api-utils'
import Vue from 'vue'
import {io} from 'socket.io-client'

const init = (whiteboard: any) => {
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
}

export default {
  init
}
