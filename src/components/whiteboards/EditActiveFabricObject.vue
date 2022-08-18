<template>
  <div>
    <div
      v-show="activeCanvasObject && !isModifyingElement"
      id="whiteboard-element-edit"
      class="darken-2 elevation-1 mx-3 rounded-pill white whiteboard-element-edit"
      :class="widthStyle"
    >
      <v-btn
        v-if="assetId"
        id="open-asset-btn"
        class="pl-2"
        color="primary"
        icon
        target="_blank"
        :href="`${$currentUser.course.assetLibraryUrl}#suitec_assetId=${assetId}`"
      >
        <span class="sr-only">Open original asset</span>
        <font-awesome-icon icon="arrow-up-right-from-square" />
      </v-btn>
      <v-btn
        id="move-layer-back-btn"
        color="primary"
        icon
        @click="changeZOrder('sendToBack')"
      >
        <span class="sr-only">Move object(s) to back</span>
        <img alt="Icon of send-to-back" class="svg-icon" src="@/assets/whiteboard/send-backward.svg" />
      </v-btn>
      <v-btn
        id="move-layer-front-btn"
        color="primary"
        icon
        @click="changeZOrder('bringToFront')"
      >
        <span class="sr-only">Move object(s) to front</span>
        <img alt="Icon of bring-to-front" class="svg-icon" src="@/assets/whiteboard/bring-forward.svg" />
      </v-btn>
      <v-btn
        id="delete-btn"
        class="pr-2"
        color="primary"
        icon
        @click="deleteActiveElements"
      >
        <span class="sr-only">Delete</span>
        <font-awesome-icon icon="trash" />
      </v-btn>
      <v-btn
        v-if="$config.isVueAppDebugMode"
        id="debug-btn"
        class="pr-2"
        color="red"
        icon
        @click="debug"
      >
        <span class="sr-only">Debug</span>
        <font-awesome-icon icon="bug" />
      </v-btn>
    </div>
  </div>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'EditActiveFabricObject',
  mixins: [Whiteboarding],
  computed: {
    assetId() {
      return this.$_.get(this.activeCanvasObject, 'assetId')
    },
    widthStyle() {
      return `${this.assetId ? 'with' : 'without'}-asset-id${this.$config.isVueAppDebugMode ? '-debug' : ''}`
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
