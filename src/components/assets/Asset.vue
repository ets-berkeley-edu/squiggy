<template>
  <div v-if="!loading">
    <BackToAssetLibrary :anchor="`asset-${asset.id}`" />

    <v-container fluid>
      <v-row justify="space-between">
        <v-col md="8">
          <h2>{{ asset.title }}</h2>
          <div v-if="asset.description">{{ asset.description }}</div>
        </v-col>
        <v-col md="4">
          <div class="d-flex">
            <div>
              <v-btn id="edit-asset-details-btn">
                <font-awesome-icon icon="pencil-alt" @click="edit" @keypress.enter="edit">Edit Details</font-awesome-icon>
              </v-btn>
            </div>
            <div>
              <v-btn id="download-asset-btn">
                <font-awesome-icon icon="download" @click="download" @keypress.enter="download">Download</font-awesome-icon>
              </v-btn>
            </div>
            <div>
              <v-btn id="delete-asset-btn">
                <font-awesome-icon icon="trash" @click="deleteAsset" @keypress.enter="deleteAsset">Download</font-awesome-icon>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>

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
import {getAsset} from '@/api/assets'

export default {
  name: 'Asset',
  components: {AssetActivityTimeline, AssetComments, AssetOverview, BackToAssetLibrary},
  mixins: [Context],
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
    }
  }
}
</script>
