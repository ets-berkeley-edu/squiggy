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
      @canvas-updated="canvasUpdated"
    >
      <FabricCircle :id="3"></FabricCircle>
    </FabricCanvas>
    <v-toolbar id="whiteboard-toolbar" dense>
      <v-card class="mr-auto" outlined tile>
        <v-btn-toggle
          v-model="selectedTool"
          multiple
        >
          <v-btn @click="setMode('move')">
            <span class="sr-only">Move and transform</span>
            <font-awesome-icon icon="mouse-pointer" />
          </v-btn>
          <v-btn title="Text" @click="setMode('text')">
            <span class="sr-only">Text</span>
            <font-awesome-icon icon="font" />
          </v-btn>
          <v-btn title="Draw" @click="setMode('draw')">
            <span class="sr-only">Draw</span>
            <font-awesome-icon icon="paint-brush" />
          </v-btn>
          <v-btn title="Shape" @click="setMode('shape')">
            <span class="sr-only">Shape</span>
            <font-awesome-icon icon="shapes" />
          </v-btn>
        </v-btn-toggle>
      </v-card>
      <v-card outlined tile>
        <v-btn-toggle v-model="selectedZoom">
          <v-btn>
            <span class="sr-only">Fit to screen</span>
            <font-awesome-icon icon="search-minus" />
          </v-btn>
          <v-btn>
            <span class="sr-only">Actual size"</span>
            <font-awesome-icon icon="search-plus" />
          </v-btn>
        </v-btn-toggle>
        <v-btn-toggle>
          <v-btn
            title="Add asset"
            @click="setMode('asset')"
          >
            <font-awesome-icon icon="circle-plus" />
            <span>Asset</span>
          </v-btn>
        </v-btn-toggle>
        <v-btn-toggle>
          <v-btn>
            <span class="sr-only">Undo</span>
            <font-awesome-icon icon="reply" />
          </v-btn>
          <v-btn>
            <span class="sr-only">Redo</span>
            <font-awesome-icon icon="share" />
          </v-btn>
        </v-btn-toggle>
        <v-btn-toggle>
          <v-btn>
            <span class="sr-only">Export</span>
            <font-awesome-icon icon="download" />
          </v-btn>
          <v-btn>
            <span class="sr-only">Settings</span>
            <font-awesome-icon icon="cog" />
          </v-btn>
        </v-btn-toggle>
      </v-card>
    </v-toolbar>
  </div>
</template>

<script>
import AddAssetsDialog from '@/components/whiteboards/AddAssetsDialog'
import Context from '@/mixins/Context'
import vueFabricWrapper from 'vue-fabric-wrapper'
import Utils from '@/mixins/Utils'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Whiteboard',
  components: {
    AddAssetsDialog,
    FabricCanvas: vueFabricWrapper.FabricCanvas,
    FabricCircle: vueFabricWrapper.FabricCircle
  },
  mixins: [Context, Utils],
  data: () => ({
    debugText: undefined,
    mode: undefined,
    selectedTool: undefined,
    selectedZoom: undefined,
    whiteboard: undefined,
    windowHeight: window.innerHeight,
    windowWidth: window.innerWidth
  }),
  watch: {
    selectedTool(newValue, oldValue) {
      console.log(`selectedTool: ${newValue} (was ${oldValue})`)
    },
    selectedZoom(newValue, oldValue) {
      console.log(`selectedZoom: ${newValue} (was ${oldValue})`)
    },
  },
  created() {
    this.$loading()
    const whiteboardId = this.$route.params.id
    // TODO: Wire up real socket IO per https://flask-socketio.readthedocs.io/
    const mockSocketId = new Date().getTime()
    getWhiteboard(whiteboardId, mockSocketId).then(data => {
      this.whiteboard = data
      this.$ready()
    })
  },
  mounted() {
    this.$nextTick(() => {
      window.addEventListener('resize', this.onResize)
    })
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize)
  },
  methods: {
    canvasUpdated(canvas) {
      console.log(canvas)
    },
    onResize() {
      this.windowHeight = window.innerHeight
      this.windowWidth = window.innerWidth
    },
    setMode(mode) {
      this.mode = mode
    }
  }
}
</script>

<style scoped>

</style>