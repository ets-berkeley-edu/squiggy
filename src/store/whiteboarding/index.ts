import _ from 'lodash'
import actions from '@/store/whiteboarding/actions'
import stateDefault from '@/store/whiteboarding/state-default'
import getters from '@/store/whiteboarding/getters'
import mutations from '@/store/whiteboarding/mutations'

export default {
  namespaced: true,
  state: _.cloneDeep(stateDefault),
  getters,
  mutations,
  actions
}
