<template>
  <v-dialog v-model="dialog">
    <template #activator="{on, attrs}">
      <v-btn
        :disabled="isModalLoading"
        v-bind="attrs"
        v-on="on"
      >
        Add asset(s)
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="pb-1">
        <h2 id="modal-header" class="title">Add asset(s)</h2>
      </v-card-title>
      <v-card-text>
        <div id="asset-library">
          <AssetsHeader ref="header" put-focus-on-load="basic-search-input" />
          <v-card class="d-flex flex-wrap" flat tile>
            <AssetCard
              v-for="(asset, index) in assetGrid"
              :key="index"
              :asset="asset"
              class="asset-card ma-3"
            />
          </v-card>
          <InfiniteLoading spinner="spiral" @infinite="infiniteHandler">
            <span slot="spinner" class="sr-only">Loading...</span>
          </InfiniteLoading>
        </div>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <div class="pb-3 pr-2">
          <v-btn
            id="save-blackout"
            color="primary"
            :disabled="disableSave"
            @click="save"
          >
            <span v-if="isSaving">
              <v-progress-circular
                class="mr-1"
                :indeterminate="true"
                rotate="5"
                size="18"
                width="2"
              />
              Saving
            </span>
            <span v-if="!isSaving">Save</span>
          </v-btn>
          <v-btn
            id="cancel-edit-of-blackout"
            text
            @click="cancel"
          >
            Cancel
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import AssetCard from '@/components/assets/AssetCard'
import AssetsHeader from '@/components/assets/AssetsHeader'
import AssetsSearch from '@/mixins/AssetsSearch'
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import Utils from '@/mixins/Utils'

export default {
  name: 'AddAssetsDialog',
  components: {AssetCard, AssetsHeader, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils],
  props: {
    onCancel: {
      required: true,
      type: Function
    },
    onSave: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    dialog: false,
    isComplete: false,
    isModalLoading: true,
    isSaving: false,
    selectedAssets: []
  }),
  computed: {
    assetGrid() {
      if (this.isModalLoading) {
        return this.getSkeletons(20)
      } else if (this.isComplete) {
        return this.assets
      } else {
        let skeletonCount = 10
        if (this.totalAssetCount && (this.totalAssetCount - this.assets.length) < skeletonCount) {
          skeletonCount = Math.max(0, this.totalAssetCount - this.assets.length)
        }
        this.nextPage()
        return (this.assets || []).concat(this.getSkeletons(skeletonCount))
      }
    },
    disableSave() {
      return !this.selectedAssets.length
    }
  },
  watch: {
    dialog(isOpen) {
      this.resetSearch()
      this.isComplete = false
      this.selectedAssets = []
      if (isOpen) {
        this.$putFocusNextTick('modal-header')
      }
    }
  },
  created() {
    this.search().then(() => {
      this.isModalLoading = false
    })
  },
  methods: {
    cancel() {
      this.dialog = false
      this.$announcer.polite('Canceled.')
      this.onCancel()
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    infiniteHandler($state) {
      if (this.$_.size(this.assets) < this.totalAssetCount) {
        this.nextPage().then(() => {
          $state.loaded()
        })
      } else {
        $state.complete()
      }
    },
    save() {
      this.isSaving = true
      this.$_.noop().then(() => {
        this.$announcer.polite('Assets added')
        this.isSaving = false
        this.dialog = false
        this.onSave()
      })
    }
  }
}
</script>
