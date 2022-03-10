<template>
  <v-dialog v-model="dialog" scrollable>
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-add-asset"
        :disabled="disableAll"
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon icon="circle-plus" size="2x" />
        <span class="pl-2">Asset</span>
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="pb-1">
        <h2 id="modal-header" class="title">Add asset(s)</h2>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text v-if="!isModalLoading" style="height: 60vh;">
        <AssetsHeader
          :hide-manage-assets-button="true"
          put-focus-on-load="basic-search-input"
        />
        <v-card class="d-flex flex-wrap" flat tile>
          <div v-for="(asset, index) in assetGrid" :key="index">
            <AssetCard
              :asset="asset"
              class="asset-card"
              context="whiteboard"
              :hide-engagement-counts="true"
              :on-asset-click="asset => selectedAssetIds.push(asset.id)"
            >
              <v-checkbox
                v-model="selectedAssetIds"
                class="mb-0 pt-0"
                dark
                :value="asset.id"
              >
                <template #label>
                  <div class="asset-checkbox-label">
                    {{ asset.title }}, by {{ oxfordJoin($_.map(asset.users, 'canvasFullName')) }}
                  </div>
                </template>
              </v-checkbox>
            </AssetCard>
          </div>
        </v-card>
      </v-card-text>
      <v-card-actions class="pt-5">
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
        <InfiniteLoading spinner="spiral" @infinite="infiniteHandler">
          <span slot="spinner" class="sr-only">Loading...</span>
        </InfiniteLoading>
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
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'AddAssetsTool',
  components: {AssetCard, AssetsHeader, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils, Whiteboarding],
  data: () => ({
    dialog: false,
    isComplete: false,
    isModalLoading: true,
    isSaving: false,
    selectedAssetIds: []
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
      return this.isModalLoading || !this.$_.size(this.selectedAssetIds)
    }
  },
  watch: {
    dialog(isOpen) {
      this.resetSearch()
      this.isComplete = false
      this.selectedAssetIds = []
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
      if (this.selectedAssetIds.length) {
        this.isSaving = true
        const whiteboardElements = this.$_.map(this.selectedAssetIds, assetId => ({
          assetId,
          element: {}
        }))
        this.saveWhiteboardElements(whiteboardElements).then(() => {
          this.$announcer.polite('Assets added')
          this.isSaving = false
          this.dialog = false
        })
      }
    }
  }
}
</script>

<style scoped>
.asset-checkbox-label {
  max-width: 240px;
}
</style>
