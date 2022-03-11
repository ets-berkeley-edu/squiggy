<template>
  <v-card v-if="!isLoading">
    <FabricCanvas
      v-if="canvas"
      :height="canvas.height"
      :stateful="true"
      :width="canvas.width"
      @mouse-down="onMousedownCanvas"
    >
      <FabricEllipse
        v-for="(ellipse, index) in $_.filter($_.map(board.whiteboardElements, 'element'), ['type', 'shape'])"
        :id="`shape-element-${index}`"
        :key="index"
      />
      <FabricText
        v-for="(element, index) in $_.filter($_.map(board.whiteboardElements, 'element'), ['type', 'text'])"
        :id="`text-element-${index}`"
        :key="index"
        :fill="element.fill"
        :font-size="element.fontSize"
        :text="element.text"
      />
    </FabricCanvas>
    <div id="toolbar" class="text-center">
      <Toolbar />
    </div>
  </v-card>
</template>

<script>
import Context from '@/mixins/Context'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import vueFabricWrapper from 'vue-fabric-wrapper'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {
    FabricCanvas: vueFabricWrapper.FabricCanvas,
    FabricEllipse: vueFabricWrapper.FabricEllipse,
    FabricText: vueFabricWrapper.FabricText,
    Toolbar
  },
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
