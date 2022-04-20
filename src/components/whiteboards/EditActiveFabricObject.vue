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
        :to="`${$currentUser.course.assetLibraryUrl}#suitec_assetId=${activeCanvasObject.assetId}`"
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
    </div>
  </div>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'EditActiveFabricObject',
  mixins: [Whiteboarding]
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
