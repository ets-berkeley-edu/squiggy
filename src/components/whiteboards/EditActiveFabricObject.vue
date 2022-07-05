<template>
  <div>
    <div
      v-show="activeCanvasObject && !isModifyingElement"
      id="whiteboard-element-edit"
      class="whiteboard-element-edit"
    >
      <v-btn
        v-if="$_.get(activeCanvasObject, 'assetId')"
        id="open-asset-btn"
        icon
        target="_blank"
        :href="`${$currentUser.course.assetLibraryUrl}#suitec_assetId=${activeCanvasObject.assetId}`"
      >
        <span class="sr-only">Open original asset</span>
        <font-awesome-icon icon="arrow-up-right-from-square" />
      </v-btn>
      <v-btn
        id="move-layer-back-btn"
        icon
        @click="moveLayer('back')"
      >
        <span class="sr-only">Move to back</span>
        <font-awesome-icon icon="arrow-down" />
      </v-btn>
      <v-btn
        id="move-layer-front-btn"
        icon
        @click="moveLayer('front')"
      >
        <span class="sr-only">Bring to front</span>
        <font-awesome-icon icon="arrow-up" />
      </v-btn>
      <v-btn
        id="delete-btn"
        icon
        @click="deleteActiveElements"
      >
        <span class="sr-only">Delete</span>
        <font-awesome-icon icon="trash" />
      </v-btn>
      <v-btn
        v-if="$config.isVueAppDebugMode"
        id="debug-btn"
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
.whiteboard-element-edit {
  display: inline-block;
  position: absolute;
  text-align: left;
  width: 180px;
  z-index: 1100;
}
</style>
