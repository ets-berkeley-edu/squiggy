<template>
  <v-card v-if="!isLoading">
    <div class="sr-only">
      <AddAssetsDialog
        :hide-managed-assets-button="true"
        :on-cancel="$_.noop"
        :on-save="$_.noop"
      />
    </div>
    <FabricCanvas
      v-if="canvas"
      :height="canvas.height"
      :stateful="true"
      :width="canvas.width"
      @mouse-down="onMousedownCanvas"
    >
      <FabricEllipse
        v-for="(ellipse, index) in $_.filter(elementJsons, ['type', 'ellipsis'])"
        :id="`ellipse-element-${index}`"
        :key="index"
      />
      <FabricText
        v-for="(element, index) in $_.filter(elementJsons, ['type', 'text'])"
        :id="`text-element-${index}`"
        :key="index"
        :fill="element.fill"
        :font-size="element.fontSize"
        :text="element.text"
      />
    </FabricCanvas>
    <div class="text-center">
      <Toolbar />
    </div>
  </v-card>
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
        this.saveElement(element).then(() => {
          this.setUnsavedFabricElement(undefined)
        })
      }
    }
  }
}
</script>
