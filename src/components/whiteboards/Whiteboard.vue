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
      background-color="pink"
      :height="windowHeight - 50"
      :stateful="true"
      :width="windowWidth"
    >
      <FabricCircle :id="3"></FabricCircle>
    </FabricCanvas>
    <WhiteboardToolbar />
  </div>
</template>

<script>
import AddAssetsDialog from '@/components/whiteboards/AddAssetsDialog'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import vueFabricWrapper from 'vue-fabric-wrapper'
import WhiteboardToolbar from '@/components/whiteboards/WhiteboardToolbar'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Whiteboard',
  components: {
    AddAssetsDialog,
    FabricCanvas: vueFabricWrapper.FabricCanvas,
    FabricCircle: vueFabricWrapper.FabricCircle,
    WhiteboardToolbar
  },
  mixins: [Context, Utils, Whiteboarding],
  created() {
    this.$loading()
    this.init(this.$route.params.id).then(() => {
      this.$ready()
    })
  }
}
</script>
