<template>
  <div>
    <div
      v-show="activeCanvasObject && !isModifyingElement"
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