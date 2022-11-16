<template>
  <div>
    <div
      v-show="activeCanvasObject && !isModifyingElement"
      id="whiteboard-element-edit"
      class="darken-2 elevation-1 mx-3 rounded-pill white whiteboard-element-edit"
      :class="widthStyle"
    >
      <v-tooltip v-if="assetId" bottom>
        <template #activator="{on, attrs}">
          <label for="open-asset-btn" class="sr-only">{{ toolTips.openOriginalAsset }}</label>
          <v-btn
            id="open-asset-btn"
            class="pl-2"
            color="primary"
            icon
            v-bind="attrs"
            target="_blank"
            :href="`${$currentUser.assetLibraryUrl}#suitec_assetId=${assetId}`"
            v-on="on"
          >
            <font-awesome-icon icon="arrow-up-right-from-square" />
          </v-btn>
        </template>
        <span>{{ toolTips.openOriginalAsset }}</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template #activator="{on, attrs}">
          <label for="move-layer-back-btn" class="sr-only">{{ toolTips.sendBack }}</label>
          <v-btn
            id="move-layer-back-btn"
            color="primary"
            icon
            v-bind="attrs"
            @click="changeZOrder('sendToBack')"
            v-on="on"
          >
            <img alt="Icon of send-to-back" class="svg-icon" src="@/assets/whiteboard/send-backward.svg" />
          </v-btn>
        </template>
        <span>{{ toolTips.sendBack }}</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template #activator="{on, attrs}">
          <label for="move-layer-front-btn" class="sr-only">{{ toolTips.sendForward }}</label>
          <v-btn
            id="move-layer-front-btn"
            color="primary"
            icon
            v-bind="attrs"
            @click="changeZOrder('bringToFront')"
            v-on="on"
          >
            <img alt="Icon of bring-to-front" class="svg-icon" src="@/assets/whiteboard/bring-forward.svg" />
          </v-btn>
        </template>
        <span>{{ toolTips.sendForward }}</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template #activator="{on, attrs}">
          <label for="delete-btn" class="sr-only">{{ toolTips.deleteItem }}</label>
          <v-btn
            id="delete-btn"
            class="pr-2"
            color="primary"
            icon
            v-bind="attrs"
            @click="deleteActiveElements"
            v-on="on"
          >
            <font-awesome-icon icon="trash" />
          </v-btn>
        </template>
        <span>{{ toolTips.deleteItem }}</span>
      </v-tooltip>
      <v-tooltip v-if="$config.socketIoDebugMode" bottom>
        <template #activator="{on, attrs}">
          <label for="debug-btn" class="sr-only">{{ toolTips.debugItem }}</label>
          <v-btn
            id="debug-btn"
            class="pr-2"
            color="red"
            icon
            v-bind="attrs"
            @click="debug"
            v-on="on"
          >
            <font-awesome-icon icon="bug" />
          </v-btn>
        </template>
        <span>{{ toolTips.debugItem }}</span>
      </v-tooltip>
    </div>
  </div>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'EditActiveFabricObject',
  mixins: [Whiteboarding],
  data: () => ({
    toolTips: {
      sendBack: 'Move object(s) to back',
      sendForward: 'Move object(s) to front',
      deleteItem: 'Delete selected item(s)',
      openOriginalAsset: 'Open original asset',
      debugItem: 'Debug item(s)'
    }
  }),
  computed: {
    assetId() {
      return this.$_.get(this.activeCanvasObject, 'assetId')
    },
    widthStyle() {
      return `${this.assetId ? 'with' : 'without'}-asset-id${this.$config.socketIoDebugMode ? '-debug' : ''}`
    }
  },
  methods: {
    debug() {
      if (this.activeCanvasObject && !this.isModifyingElement) {
        console.log('\n---\n' + JSON.stringify(this.activeCanvasObject) + '\n---\n')
      }
    }
  }
}
</script>

<style scoped>
.svg-icon {
  filter: invert(51%) sepia(40%) saturate(789%) hue-rotate(160deg) brightness(90%) contrast(88%);
  width: 15px;
}
.with-asset-id-debug {
  width: 180px;
}
.with-asset-id {
  width: 150px;
}
.without-asset-id {
  width: 120px;
}
.without-asset-id-debug {
  width: 150px;
}
.whiteboard-element-edit {
  display: inline-block;
  margin-top: -5px;
  position: absolute;
  text-align: center;
  z-index: 1100;
}
</style>
