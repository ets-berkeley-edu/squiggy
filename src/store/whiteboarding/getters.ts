import _ from 'lodash'
import Vue from 'vue'

export default {
  canvas: (): any => Vue.prototype.$canvas,
  disableAll: (state: any): boolean => state.disableAll,
  fabricElementTemplates: (): any => [], // TODO: remove?
  onlineUsers: (state: any): any[] => _.filter(state.whiteboard.members, {online: true}),
  unsavedFabricElement: (state: any): any => state.unsavedFabricElement, // TODO: remove?
  whiteboard: (state: any): any => state.whiteboard,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}
