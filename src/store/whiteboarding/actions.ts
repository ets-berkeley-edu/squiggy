import _ from 'lodash'
import Vue from 'vue'
import {createWhiteboardElements, getWhiteboard, restoreWhiteboard} from '@/api/whiteboards'

const p = Vue.prototype

const $_alert = _.noop
const $modal = _.noop

const $_findElement = (state: any, uuid: number) => _.find(state.board.whiteboardElements, ['uuid', uuid])

const $_getSelectedAsset = (): any => {
  // Get the id of the currently selected asset element.
  const selectedElement = p.$canvas.getActiveObject()
  if (selectedElement) {
    return selectedElement.assetId
  }
}

export default {
  addLink: ({commit, state}) => {
    // Launch the modal that allows for a new link to be added
    // Create a new scope for the modal dialog
    const scope = state.$new(true)
    scope.closeModal = function(asset) {
      if (asset) {
        commit('addAsset', asset)
      }
      this.$hide()
    }
    // Open the add link modal dialog
    _.noop({
      scope: scope,
      template: '/app/whiteboards/addlinkmodal/addlinkmodal.html'
    })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  afterCanvasRender: ({commit}) => commit('afterCanvasRender'),
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  editWhiteboard: ({commit}) => {
    // Create a new scope for the modal dialog
    // const scope = state.$new(true)
    // scope.whiteboard = state.whiteboard
    // scope.closeModal = function(updatedWhiteboard) {
    //   if (updatedWhiteboard) {
    //     if (updatedWhiteboard.notFound) {
    //       // TODO: If an edit has removed the user's access, refresh the whiteboard list and close this whiteboard
    //       // if ($window.opener) {
    //       //   $window.opener.refreshWhiteboardList()
    //       // }
    //       // $window.close()
    //       _.noop()
    //     } else {
    //       state.whiteboard = updatedWhiteboard
    //       // TODO: Set the title of the window to the new title of the whiteboard
    //       // $rootScope.header = state.whiteboard.title
    //     }
    //   }
    //   // this.$hide()
    // }
    // TODO: Open the edit whiteboard modal dialog
    // $modal({
    //   'scope': scope,
    //   'template': '/app/whiteboards/edit/edit.html'
    // })
    // Switch the toolbar back to move mode. This will
    // also close any open popovers
    commit('setMode', 'move')
  },
  exportasassetmodal: () => {},
  exportAsAsset: ({commit, state}) => {
    // Launch the modal that allows the current user to export the current whiteboard to the asset library
    // Create a new scope for the modal dialog
    const scope = state.$new(true)
    scope.whiteboard = state.whiteboard
    scope.closeModal = function(asset) {
      if (asset) {
        // Construct the link back to the asset library
        // const assetLibraryLink = '/assetlibrary?api_domain=' + launchParams.apiDomain + '&course_id=' + launchParams.courseId + '&tool_url=' + launchParams.toolUrl
        // Show a notification indicating the whiteboard was exported
        $_alert({
          container: '#whiteboards-board-notifications',
          content: 'This board has been successfully added to the <strong>Asset Library</strong>.',
          duration: 5,
          keyboard: true,
          show: true,
          templateUrl: 'whiteboards-notification-template',
          type: 'success'
        })
      }
      this.$hide()
    }
    // Open the export as asset modal dialog
    $modal({
      scope: scope,
      templateUrl: '/app/whiteboards/exportasassetmodal/exportasasset.html'
    })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  getObjectAttribute: ({state}, {key, uuid}) => {
    const object = $_findElement(state, uuid)
    return object && object.get(key)
  },
  getSelectedAsset: () => $_getSelectedAsset(),
  getSelectedAssetParams: () => {
    // Get the parameters required to construct the URL to the asset detail page of the currently selected asset element.
    const assetId = $_getSelectedAsset()
    if (assetId) {
      return {
        // TODO:
        // 'api_domain': launchParams.apiDomain,
        // 'course_id': launchParams.courseId,
        // 'tool_url': launchParams.toolUrl,
        assetId: assetId,
        whiteboard_referral: true
      }
    }
  },
  init: ({commit}, whiteboardId: number) => {
    return getWhiteboard(whiteboardId).then(whiteboard => {
      commit('init', whiteboard)
    })
  },
  moveLayer: ({commit}, direction: string) => commit('moveLayer', direction),
  resetSelected: ({commit}) => commit('resetSelected'),
  restoreWhiteboard: ({commit, state}) => {
    if (state.whiteboard && state.whiteboard.deletedAt) {
      return restoreWhiteboard(state.whiteboard.id).then(function() {
        // Update local state
        commit('restoreWhiteboard')
        // Show a notification indicating the whiteboard was restored
        $_alert({
          container: '#whiteboards-board-notifications',
          content: 'The whiteboard has been restored.',
          duration: 5,
          keyboard: true,
          show: true,
          templateUrl: 'whiteboards-notification-template',
          type: 'success'
        })
      })
    }
  },
  reuseAsset: ({commit}) => {
    // TODO

    // Launch the modal that allows for an existing asset to be added to whiteboard canvas
    // Create a new scope for the modal dialog
    // var scope = $scope.$new(true);
    // scope.closeModal = function(selectedAssets) {
    //   _.each(selectedAssets, addAsset);
    //   this.$hide();
    //   this.$destroy();
    // };
    // Open the asset selection modal dialog
    // $modal({
    //   'animation': false,
    //   'scope': scope,
    //   'template': '/app/whiteboards/reuse/reuse.html'
    // })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  saveWhiteboardElements: ({commit, state}: any, whiteboardElements: any[]) => {
    return new Promise<void>(resolve => {
      commit('setDisableAll', true)
      return createWhiteboardElements(whiteboardElements, state.whiteboard.id)
      .then(data => _.get(data, 'element'))
      .then(data => {
        _.each(data, whiteboardElement => commit('add', whiteboardElement))
        commit('setDisableAll', false)
        return resolve()
      })
    })
  },
  setDisableAll: ({commit}, disableAll: boolean) => commit('setDisableAll', disableAll),
  setIsModifyingElement: ({commit}, isModifyingElement: boolean) => commit('setIsModifyingElement', isModifyingElement),
  setIsScrollingCanvas: ({commit}, isScrollingCanvas: boolean) => commit('setIsScrollingCanvas', isScrollingCanvas),
  setMode: ({commit}, mode: string) => commit('setMode', mode),
  toggleZoom: ({commit}) => commit('toggleZoom'),
  updateSelected: ({commit}, properties: any) => commit('updateSelected', properties),
  uploadFiles: ({commit}) => {
    // TODO: Create a new scope for the modal dialog

    // scope.closeModal = function(assets) {
    //   _.each(assets, addAsset)
    //   this.$hide()
    // }
    // // Open the add link modal dialog
    // $modal({
    //   'scope': scope,
    //   'template': '/app/whiteboards/uploadmodal/uploadmodal.html'
    // })
    // Switch the toolbar back to move mode. This will
    // also close the add asset popover
    commit('setMode', 'move')
  }
}
