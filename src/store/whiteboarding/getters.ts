import _ from 'lodash'
import constants from '@/store/whiteboarding/utils/constants'

export default {
  colors: (): any => constants.COLORS,
  disableAll: (state: any): boolean => state.disableAll,
  mode: (state: any): string => state.mode,
  onlineUsers: (state: any): any[] => _.filter(state.whiteboard.members, {online: true}),
  selected: (state: any): any => state.selected,
  textSizeOptions: (): any => constants.TEXT_SIZE_OPTIONS,
  whiteboard: (state: any): any => state.whiteboard,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}
