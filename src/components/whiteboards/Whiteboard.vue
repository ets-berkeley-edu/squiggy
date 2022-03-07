<template>
  <div v-if="!isLoading">
    <div class="sr-only">
      <AddAssetsDialog
        :hide-managed-assets-button="true"
        :on-cancel="$_.noop"
        :on-save="$_.noop"
      />
    </div>
    <FabricCanvas
      :background-color="canvas.backgroundColor"
      :height="canvas.height"
      :stateful="true"
      :width="canvas.width"
    >
      <FabricEllipse
        v-for="(ellipse, index) in ellipsisElements"
        :id="`ellipse-element-${index}`"
        :key="index"
      />
      <FabricText
        v-for="(element, index) in textElements"
        :id="`text-element-${index}`"
        :key="index"
        :fill="element.fill"
        :text="element.text"
      />
    </FabricCanvas>
    <Toolbar />
  </div>
</template>

<script>
import AddAssetsDialog from '@/components/whiteboards/AddAssetsDialog'
import Context from '@/mixins/Context'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import vueFabricWrapper from 'vue-fabric-wrapper'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {
    AddAssetsDialog,
    FabricCanvas: vueFabricWrapper.FabricCanvas,
    FabricEllipse: vueFabricWrapper.FabricEllipse,
    FabricText: vueFabricWrapper.FabricText,
    Toolbar
  },
  computed: {
    canvas() {
      return this.elementJsons.find(e => e.type === 'canvas')
    },
    ellipsisElements() {
      return this.$_.filter(this.elementJsons, ['type', 'ellipsis'])
    },
    textElements() {
      return this.$_.filter(this.elementJsons, ['type', 'text'])
    }
  },
  created() {
    this.$loading()
    this.init(this.$route.params.id).then(() => {
      this.$ready()
    })
  }
}
</script>
