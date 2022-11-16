<template>
  <div :id="idPrefix">
    <h2 class="impact-studio-section-header my-3">
      {{ title }}
    </h2>
    <v-row v-if="assets.length || orderBy !== 'recent'" no-gutters class="mb-4">
      <div class="px-4 d-flex align-center">
        Sort by
      </div>
      <select :id="`${idPrefix}-sort-select`" v-model="orderBy" class="native-select mr-4">
        <option v-for="(optionText, optionValue) in $config.orderByOptions" :key="optionValue" :value="optionValue">
          {{ optionText }}
        </option>
      </select>
      <v-btn
        :id="`${idPrefix}-sort-apply`"
        color="primary"
        @click="sortAssets(orderBy)"
        @keypress.enter.prevent="sortAssets(orderBy)"
      >
        Apply
      </v-btn>
    </v-row>
    <v-card
      v-if="assets.length"
      :id="`${idPrefix}-assets-lane`"
      class="d-flex flex-wrap"
      flat
      tile
    >
      <AssetCard
        v-for="(asset, index) in assets"
        :key="index"
        :asset="asset"
        :on-asset-click="goToAsset(asset)"
        class="asset-card ma-3"
      />
      <div v-if="showMore" class="asset-card ma-3 d-flex align-center" align-center>
        <a :id="`${idPrefix}-view-all-link`" :href="assetsHref">
          View all assets in the Asset Library
        </a>
      </div>
    </v-card>
    <div v-if="!assets.length" :id="`${idPrefix}-no-assets-msg`" class="px-4">
      No assets.
    </div>
  </div>
</template>

<script>
import AssetCard from '@/components/assets/AssetCard'
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetSwimlane',
  components: {AssetCard},
  mixins: [Utils],
  props: {
    assets: {
      required: true,
      type: Array,
    },
    fetchAssets: {
      required: true,
      type: Function,
    },
    idPrefix: {
      required: true,
      type: String
    },
    showMore: {
      required: true,
      type: Boolean
    },
    title: {
      required: true,
      type: String
    },
    user: {
      required: false,
      type: Object,
      default: null
    }
  },
  data: () => ({
    orderBy: 'recent'
  }),
  computed: {
    assetsHref() {
      let hash = `suitec_orderBy=${this.orderBy}`
      if (this.user) {
        hash = `suitec_userId=${this.user.id}&${hash}`
      }
      if (this.$isInIframe) {
        return this.$currentUser.assetLibraryUrl + '#' + hash
      } else {
        return '/assets#' + hash
      }
    }
  },
  methods: {
    goToAsset(asset) {
      return () => this.go(`/asset/${asset.id}`, {from: 'impactStudio'})
    },
    sortAssets() {
      this.fetchAssets(this.orderBy).then(() => this.$announcer.polite(`Resorted assets by ${this.orderBy}`))
    }
  },
  created() {
    this.fetchAssets(this.orderBy)
  }
}
</script>
