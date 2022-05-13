<template>
  <v-dialog
    v-model="dialog"
    fullscreen
    scrollable
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-add-existing-assets"
        :color="mode === 'assets' ? 'white' : 'primary'"
        icon
        :title="title"
        value="assets"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">{{ title }}</span>
        <font-awesome-icon
          :color="{'white': mode === 'assets'}"
          icon="images"
          size="lg"
        />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="pb-1">
        <h2 id="modal-header" class="title">Select Asset(s)</h2>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <div v-if="totalAssetCount === 0">
          <h3 id="no-existing-assets" class="px-3 py-8">There are no existing assets to add.</h3>
        </div>
        <AssetsHeader
          v-if="totalAssetCount > 1"
          :hide-manage-assets-button="true"
          put-focus-on-load="basic-search-input"
        />
        <v-card class="d-flex flex-wrap" flat tile>
          <div
            v-for="(asset, index) in assetGrid"
            :key="index"
            class="ma-3"
          >
            <AssetCard
              :asset="asset"
              class="asset-card"
              context="whiteboard"
              :hide-engagement-counts="true"
              :on-asset-click="asset => selectedAssetIds.push(asset.id)"
            >
              <v-checkbox
                :id="`asset-${asset.id}`"
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
      <v-card-actions v-if="isDialogReady" class="pt-5">
        <v-spacer></v-spacer>
        <div class="pb-3 pr-2">
          <v-btn
            id="save-btn"
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
              Saving {{ dialog }}
            </span>
            <span v-if="!isSaving">Save</span>
          </v-btn>
          <v-btn
            id="cancel-btn"
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
  name: 'AddExistingAssets',
  components: {AssetCard, AssetsHeader, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils, Whiteboarding],
  data: () => ({
    allAssetsLoaded: false,
    dialog: false,
    isDialogReady: false,
    isSaving: false,
    selectedAssetIds: [],
    title: 'Add existing assets'
  }),
  computed: {
    assetGrid() {
      if (this.isDialogReady) {
        if (this.allAssetsLoaded) {
          return this.assets
        } else {
          let skeletonCount = 10
          if (this.totalAssetCount && (this.totalAssetCount - this.assets.length) < skeletonCount) {
            skeletonCount = Math.max(0, this.totalAssetCount - this.assets.length)
          }
          this.nextPage()
          return (this.assets || []).concat(this.getSkeletons(skeletonCount))
        }
      } else {
        return this.getSkeletons(20)
      }
    },
    disableSave() {
      return !this.isDialogReady || !this.$_.size(this.selectedAssetIds)
    }
  },
  watch: {
    dialog(value) {
      this.resetSearch()
      this.allAssetsLoaded = false
      this.selectedAssetIds = []
      if (value) {
        this.search().then(() => {
          if (!this.totalAssetCount) {
            this.allAssetsLoaded = true
          }
          this.isDialogReady = true
          this.$putFocusNextTick('modal-header')
        })
      } else {
        this.reset()
      }
    }
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled.')
      this.reset()
      this.dialog = false
      this.isDialogReady = false
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    infiniteHandler($state) {
      if (this.isSaving || !this.dialog) {
        $state.complete()
      } else {
        this.allAssetsLoaded = this.$_.size(this.assets) >= this.totalAssetCount
        if (this.allAssetsLoaded) {
          $state.complete()
        } else {
          this.nextPage().then(() => $state.loaded())
        }
      }
    },
    reset() {
      this.allAssetsLoaded = false
      this.isDialogReady = false
      this.isSaving = false
      this.selectedAssetIds = []
    },
    save() {
      if (this.selectedAssetIds.length) {
        this.isSaving = true
        const assetIds = this.$_.uniq(this.selectedAssetIds)
        this.$_.each(assetIds, (assetId, index) => {
          const asset = this.$_.find(this.assets, ['id', assetId])
          this.addAsset(asset)
          if (index === assetIds.length - 1) {
            this.$announcer.polite('Assets added')
            this.isSaving = false
            this.dialog = false
            this.reset()
          }
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
