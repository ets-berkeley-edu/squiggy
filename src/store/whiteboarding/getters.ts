import _ from 'lodash'

export default {
  disableAll: (state: any): boolean => state.disableAll,
  mode: (state: any): string => state.mode,
  onlineUsers: (state: any): any[] => _.filter(state.whiteboard.members, {online: true}),
  whiteboard: (state: any): any => state.whiteboard,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}
