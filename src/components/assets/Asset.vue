<template>
  <div v-if="!loading">
    <BackToAssetLibrary :anchor="`asset-${asset.id}`" />

    <div class="d-flex justify-space-between w-100">
      <div>
        <h2>{{ asset.title }}</h2>
        <div v-if="asset.description">{{ asset.description }}</div>
      </div>
      <div class="d-flex align-content-end">
        <div class="mr-2">
          <v-btn
            id="edit-asset-details-btn"
            class="text-no-wrap"
            @click="edit"
            @keypress.enter="edit"
          >
            <font-awesome-icon class="mr-2" icon="pencil-alt" />
            Edit Details
          </v-btn>
        </div>
        <div class="mr-2">
          <v-btn id="download-asset-btn" @click="download" @keypress.enter="download">
            <font-awesome-icon class="mr-2" icon="download" />
            Download
          </v-btn>
        </div>
        <div>
          <v-btn
            id="delete-asset-btn"
            class="mr-3"
            @click="deleteAsset"
            @keypress.enter="deleteAsset"
          >
            <font-awesome-icon class="mr-2" icon="trash" />
            Delete
          </v-btn>
        </div>
      </div>
    </div>

    <AssetOverview :asset="asset" />

    <AssetActivityTimeline :asset="asset" />

    <AssetComments :asset="asset" />

    <pre>
      {{ asset }}
    </pre>
  </div>
</template>

<script>
import AssetActivityTimeline from '@/components/assets/AssetActivityTimeline'
import AssetComments from '@/components/assets/AssetComments'
import AssetOverview from '@/components/assets/AssetOverview'
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAsset} from '@/api/assets'

export default {
  name: 'Asset',
  components: {AssetActivityTimeline, AssetComments, AssetOverview, BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    asset: undefined
  }),
  created() {
    this.$loading()
    getAsset(this.$route.params.id).then(data => {
      this.asset = data
      this.$ready(this.asset.title)
    })
  },
  methods: {
    deleteAsset() {
      this.$announcer.polite(`Confirm delete asset ${this.asset.title}`)
    },
    download() {
      this.$announcer.polite(`Downloading asset ${this.asset.title}`)
    },
    edit() {
      this.$announcer.polite(`Edit asset ${this.asset.title}`)
      this.go(`/asset/${this.asset.id}/edit`)
    }
  }
}
</script>
