<template>
  <v-dialog
    v-model="dialog"
    fullscreen
  >
    <template #activator="activator">
      <v-tooltip bottom :disabled="mode === 'assets'">
        <template #activator="tooltip">
          <v-btn
            id="toolbar-add-existing-assets"
            :alt="tooltipText"
            :color="mode === 'assets' ? 'white' : 'primary'"
            icon
            value="assets"
            v-bind="activator.attrs"
            v-on="{...activator.on, ...tooltip.on}"
          >
            <font-awesome-icon
              :color="{'white': mode === 'assets'}"
              icon="folder-open"
              size="lg"
            />
          </v-btn>
        </template>
        <span>{{ tooltipText }}</span>
      </v-tooltip>
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
          :open-advanced-search="!!(assetType || categoryId || (orderBy !== orderByDefault) || userId)"
          put-focus-on-load="basic-search-input"
        />
        <v-card class="d-flex flex-wrap" flat tile>
          <div
            v-for="(asset, index) in assetGrid"
            :key="index"
            class="ma-3"
          >
            <AssetCard
              :aria-pressed="selectedAssetIds.includes(asset.id)"
              :asset="asset"
              class="asset-card"
              context="whiteboard"
              :hide-engagement-counts="true"
              :on-asset-click="onClickAssetImage"
            >
              <v-checkbox
                :id="`asset-${asset.id}`"
                v-model="selectedAssetIds"
                class="mb-0 pt-0"
                dark
                multiple
                readonly
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
        <div class="font-weight-bold pl-3 text--secondary">
          {{ selectedAssetIds.length }} selected
        </div>
        <v-spacer></v-spacer>
        <div class="pb-3 pr-2">
          <v-btn
            id="save-btn"
            color="primary"
            :disabled="disableSave"
            @click="save"
          >
            <span v-if="isSaving" class="mt-1">
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
            id="cancel-btn"
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
import InfiniteScrolling from '@/mixins/InfiniteScrolling'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'AddExistingAssets',
  components: {AssetCard, AssetsHeader},
  mixins: [AssetsSearch, Context, InfiniteScrolling, Utils, Whiteboarding],
  data: () => ({
    dialog: false,
    isComplete: false,
    isDialogReady: false,
    isSaving: false,
    selectedAssetIds: [],
    tooltipText: 'Add existing assets'
  }),
  computed: {
    assetGrid() {
      if (!this.isDialogReady) {
        return this.getSkeletons(20)
      } else if (this.isComplete) {
        return this.assets
      } else {
        let skeletonCount = 10
        if (this.totalAssetCount && (this.totalAssetCount - this.assets.length) < skeletonCount) {
          skeletonCount = Math.max(0, this.totalAssetCount - this.assets.length)
        }
        return (this.assets || []).concat(this.getSkeletons(skeletonCount))
      }
    },
    disableSave() {
      return !this.isDialogReady || !this.$_.size(this.selectedAssetIds)
    }
  },
  watch: {
    dialog(value) {
      this.resetSearch()
      this.stopInfiniteLoading()
      this.isComplete = false
      this.selectedAssetIds = []
      if (value) {
        this.initAssetSearchOptions().then(() => {
          this.search().then(() => {
            if (!this.totalAssetCount) {
              this.isComplete = true
            } else {
              this.checkAssetsLoaded()
              if (!this.isComplete) {
                this.startInfiniteLoading(this.fetch, {dialog: true, threshold: 800})
              }
            }
            this.isDialogReady = true
            this.$putFocusNextTick('modal-header')
          })
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
    checkAssetsLoaded() {
      if (!this.isComplete && this.$_.size(this.assets) >= this.totalAssetCount) {
        this.isComplete = true
      }
    },
    fetch() {
      return this.nextPage().then(data => {
        if (data.results.length) {
          this.$announcer.polite(`${this.assets.length} of ${this.totalAssetCount} assets loaded.`)
        } else {
          this.isComplete = true
          this.$announcer.polite(`All ${this.totalAssetCount} assets have loaded.`)
        }
        this.checkAssetsLoaded()
      })
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    onClickAssetImage(asset) {
      if (this.selectedAssetIds.includes(asset.id)) {
        this.selectedAssetIds = this.$_.filter(this.selectedAssetIds, id => id !== asset.id)
      } else {
        this.selectedAssetIds.push(asset.id)
      }
    },
    reset() {
      this.isComplete = false
      this.isDialogReady = false
      this.isSaving = false
      this.selectedAssetIds = []
      this.stopInfiniteLoading()
    },
    save() {
      if (this.selectedAssetIds.length) {
        this.isSaving = true
        const assetIds = this.$_.uniq(this.selectedAssetIds)
        const assets = this.$_.map(assetIds, assetId => {
          return this.$_.find(this.assets, ['id', assetId])
        })
        this.addAssets(assets).then(() => {
          this.$announcer.polite('Assets added')
          this.isSaving = false
          this.dialog = false
          this.reset()
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
