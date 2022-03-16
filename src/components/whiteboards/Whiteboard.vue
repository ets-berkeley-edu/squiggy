<template>
  <div id="whiteboard-container" class="whiteboard-container">
    <div id="whiteboard-viewport" class="whiteboard-viewport">
      <canvas id="canvas"></canvas>
    </div>
    <!--
    <div id="whiteboard-edit-controls" data-ng-show="isElementSelected() && !isModifyingElement">
      <v-btn
        v-if="getSelectedAsset()"
        title="Open original asset"
        target="_blank"
        ui-sref="assetlibrarylist.item(getSelectedAssetParams())"
      >
        <i class="fa fa-external-link"><span class="sr-only">Open original asset</span></i>
      </v-btn>
      <div class="btn-group" role="group">
        <v-btn
          title="Move to back"
          data-ng-click="moveLayer('back')"
        >
          <i class="fa fa-arrow-down"><span class="sr-only">Move to back</span></i>
        </v-btn>
        <v-btn
          title="Bring to front"
          data-ng-click="moveLayer('front')"
        >
          <i class="fa fa-arrow-up"><span class="sr-only">Bring to front</span></i>
        </v-btn>
      </div>
      <v-btn
        title="Delete"
        @click="deleteActiveElements"
      >
        <i class="fa fa-trash"><span class="sr-only">Delete</span></i>
      </v-btn>
    </div>
    -->

    <!-- EXPORT POPOVER
    <script type="text/ng-template" id="exportPopoverTemplate">
      <ul class="whiteboards-popover-button-list whiteboards-popover-export">
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="exportAsAsset()" data-ng-disabled="getNumberOfElements() === 0">
            <i class="fa fa-th"></i> Export to Asset Library
          </button>
        </li>
        <li class="clearfix">
          <a class="btn btn-default" data-ng-href="{{exportPngUrl}}" data-ng-click="exportAsPng($event)" data-ng-disabled="isExportingAsPng || getNumberOfElements() === 0">
            <span data-ng-if="isExportingAsPng"><i class="fa fa-spin fa-spinner"></i> Downloading image</span>
            <span data-ng-if="!isExportingAsPng"><i class="fa fa-download"></i> Download as image</span>
          </a>
        </li>
      </ul>
    </script>
    -->
    <!-- ADD ASSET POPOVER
    <script type="text/ng-template" id="addAssetPopoverTemplate">
      <ul class="whiteboards-popover-button-list whiteboards-popover-asset">
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="reuseAsset()">
            <i class="fa fa-th"></i> Use existing
          </button>
        </li>
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="uploadFiles()">
            <i class="fa fa-laptop"></i> Upload New
          </button>
        </li>
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="addLink()">
            <i class="fa fa-link"></i> Add Link
          </button>
        </li>
      </ul>
    </script>
    -->
    <!-- SIDEBAR BUTTONS
    <div id="whiteboard-sidebar-buttons" data-ng-class="{'whiteboard-sidebar-expanded': sidebarExpanded}"  data-ng-if="!readonly">
      <button type="button" class="btn btn-link whiteboard-toolbar-collaborators" title="Collaborators" data-ng-click="toggleSidebar('online')" data-ng-class="{'active': sidebarExpanded && sidebarMode === 'online'}">
        <i class="fa fa-user">
          <span class="sr-only">Collaborators</span>
        </i>
        <span class="badge" data-ng-bind="getOnlineUsers().length"></span>
      </button>
      <button type="button" class="btn btn-link whiteboard-toolbar-chat" title="Chat" data-ng-click="toggleSidebar('chat')" data-ng-class="{'active': sidebarExpanded && sidebarMode === 'chat'}">
        <i class="fa fa-comments">
          <span class="sr-only">Chat</span>
        </i>
      </button>
    </div>
    -->
    <!-- ADD ASSET POPOVER
    <template id="addAssetPopoverTemplate">
      <ul class="whiteboards-popover-button-list whiteboards-popover-asset">
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="reuseAsset()">
            <i class="fa fa-th"></i> Use existing
          </button>
        </li>
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="uploadFiles()">
            <i class="fa fa-laptop"></i> Upload New
          </button>
        </li>
        <li class="clearfix">
          <button class="btn btn-default" data-ng-click="addLink()">
            <i class="fa fa-link"></i> Add Link
          </button>
        </li>
      </ul>
    </template>
     -->
    <div v-if="whiteboard && !whiteboard.deletedAt" id="toolbar" class="text-center">
      <Toolbar />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {Toolbar},
  created() {
    this.$loading()
    this.init(this.$route.params.id).then(() => {
      this.$ready()
    })
  },
  methods: {
    onMousedownCanvas(event) {
      if (this.unsavedFabricElement) {
        console.log(`TODO: Capture position from ${event} object`)
        const element = {
          ...this.unsavedFabricElement,
          ...{
            text: 'Hello World',
          }
        }
        this.saveWhiteboardElements([{element}]).then(() => {
          this.setUnsavedFabricElement(undefined)
        })
      }
    }
  }
}
</script>

<style scoped>
.whiteboard-container {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  z-index: 1000;
}
.whiteboard-viewport {
  height: 100%;
  overflow: scroll;
  position: relative;
  width: 100%;
}
</style>
