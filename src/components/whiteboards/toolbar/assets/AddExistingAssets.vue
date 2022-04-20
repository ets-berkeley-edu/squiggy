<template>
  <v-dialog
    v-model="dialog"
    scrollable
    transition="dialog-bottom-transition"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-add-existing-assets"
        class="justify-start w-100"
        text
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon icon="bars" size="2x" />
        <span class="pl-3">Use existing</span>
      </v-btn>
    </template>
    <v-card class="active-card">
      <v-card-title class="pb-1">
        <h2 id="modal-header" class="title">Select Asset(s)</h2>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <AssetsHeader
          v-if="totalAssetCount > 1"
          :hide-manage-assets-button="true"
          put-focus-on-load="basic-search-input"
        />
        <v-card class="d-flex flex-wrap" flat tile>
          <div
            v-for="(asset, index) in assetGrid"
            :key="index"
            class="mt-4"
          >
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
      <v-card-actions v-if="isDialogReady" class="pt-5">
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
  name: 'AddExistingAssets',
  components: {AssetCard, AssetsHeader, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils, Whiteboarding],
  props: {
    watchDialog: {
      default: () => {},
      required: false,
      type: Function
    }
  },
  data: () => ({
    dialog: false,
    isComplete: false,
    isDialogReady: false,
    isSaving: false,
    selectedAssetIds: []
  }),
  computed: {
    assetGrid() {
      if (this.isDialogReady) {
        if (this.isComplete) {
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
      this.isComplete = false
      this.selectedAssetIds = []
      if (value) {
        this.search().then(() => {
          this.isDialogReady = true
          this.$putFocusNextTick('modal-header')
        })
      } else {
        this.cancel()
      }
      this.watchDialog(value)
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
      this.isComplete = this.$_.size(this.assets) >= this.totalAssetCount
      if (this.isComplete) {
        $state.complete()
      } else {
        this.nextPage().then(() => $state.loaded())
      }
    },
    reset() {
      this.isSaving = false
      this.dialog = false
      this.selectedAssetIds = []
    },
    save() {
      if (this.selectedAssetIds.length) {
        this.isSaving = true
        this.selectedAssetIds.forEach((assetId, index) => {
          const asset = this.$_.find(this.assets, ['id', assetId])
          this.addAsset(asset)
          if (index === this.selectedAssetIds.length - 1) {
            this.$announcer.polite('Assets added')
            this.reset()
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.active-card {
  left: 0;
  position: fixed;
  top: 0;
}
.asset-checkbox-label {
  max-width: 240px;
}
</style>
