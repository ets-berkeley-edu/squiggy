<template>
  <div v-if="canvas">
    <div
      v-show="canvas && canvas.getActiveObject() && !isModifyingElement"
      id="whiteboard-element-edit"
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
      <v-btn-toggle
        v-model="moveLayer"
        rounded
      >
        <v-btn @click="moveLayer('back')">
          moveLayer('back')
        </v-btn>
        <v-btn @click="moveLayer('front')">
          moveLayer('front')
        </v-btn>
      </v-btn-toggle>
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
