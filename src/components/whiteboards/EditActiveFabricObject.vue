<template>
  <div>
    <div
      v-show="canvas && canvas.getActiveObject() && !isModifyingElement"
      id="whiteboard-element-edit"
      class="whiteboard-element-edit"
    >
      <v-btn
        v-if="selectedAsset"
        class="btn btn-default"
        text
        title="Open original asset"
        target="_blank"
      >
        <i class="fa fa-external-link"><span class="sr-only">Open original asset</span></i>
      </v-btn>
      <v-btn
        id="move-layer-back-btn"
        icon
        @click="moveLayer('back')"
      >
        <span class="sr-only">Move back</span>
        <font-awesome-icon icon="arrow-down" />
      </v-btn>
      <v-btn @click="moveLayer('front')">
        moveLayer('front')
      </v-btn>
      <v-btn @click="deleteActiveElements">
        Delete
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
  width: 140px;
  z-index: 1100;
}
.whiteboard-element-edit .btn-default {
  padding: 5px 8px;
}
.whiteboard-element-edit .btn-default:not(:hover) {
  background-color: #FFF;
}
.whiteboard-element-edit .btn-default i {
  color: #666;
  font-size: 17px;
}
.whiteboard-element-edit .btn-default i.fa-external-link {
  left: 1px;
  position: relative;
  top: 2px;
}
</style>
