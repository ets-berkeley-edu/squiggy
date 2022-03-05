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
      <FabricEllipse
        v-for="(ellipse, index) in board.ellipses"
        :id="`ellipse=${index}`"
        :key="index"
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
    Toolbar
  },
  created() {
    this.$loading()
    this.init(this.$route.params.id).then(() => {
      this.$ready()
    })
  }
}
</script>
