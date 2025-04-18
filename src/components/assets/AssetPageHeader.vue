<template>
  <div class="align-content-center flex-wrap d-flex justify-space-between pt-2 w-100">
    <PageTitle class="text-break mr-2" :text="asset.title" />
    <div class="d-flex align-content-end">
      <div v-if="downloadUrl" class="mr-2">
        <v-btn id="download-asset-btn" @click="downloadAsset" @keypress.enter.prevent="downloadAsset">
          <font-awesome-icon class="mr-2" icon="download" />
          Download
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetPageHeader',
  mixins: [Utils],
  components: {PageTitle},
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    downloadUrl: undefined
  }),
  created() {
    if (this.asset.assetType === 'file') {
      this.downloadUrl = `${this.$config.apiBaseUrl}/api/asset/${this.asset.id}/download`
    }
  },
  methods: {
    downloadAsset() {
      window.location.href = this.downloadUrl
    }
  }
}
</script>
