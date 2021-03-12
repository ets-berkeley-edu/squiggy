<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-row justify="space-between">
          <v-col v-for="user in asset.users" :key="user.id">
            by [face here] <a href="#">{{ user.canvasFullName }}</a> on {{ asset.createdAt | moment('lll') }}
          </v-col>
          <v-col>
            <v-row align="center" justify="end">
              <div class="mr-3">
                <v-btn
                  id="like-asset-btn"
                  icon
                  @click="like"
                  @keypress.enter.prevent="like"
                >
                  <font-awesome-icon icon="thumbs-up" />
                  <span id="asset-like-count" class="ml-1">{{ asset.likes }}</span>
                </v-btn>
              </div>
              <div class="mr-5">
                <font-awesome-icon icon="eye" />
                <span id="asset-view-count" class="ml-1">{{ asset.views }}</span>
              </div>
              <div class="mr-3">
                <font-awesome-icon icon="comment" />
                <span id="asset-comment-count" class="ml-1">{{ asset.commentCount }}</span>
              </div>
            </v-row>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-img :src="imageUrl" width="500">
          <template #placeholder>
            <v-row class="fill-height ma-0" align="center" justify="center">
              <v-progress-circular indeterminate color="grey lighten-5" />
            </v-row>
          </template>
        </v-img>
        <v-divider class="my-2" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        Description
      </v-col>
      <v-col>
        {{ asset.description }}
      </v-col>
      <v-col>
        Source
      </v-col>
      <v-col>
        {{ asset.source || '&mdash;' }}
      </v-col>
    </v-row>
    <v-row justify="start">
      <v-col>
        Category
      </v-col>
      <v-col>
        {{ asset.categories }}
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import {likeAsset} from '@/api/assets'

export default {
  name: 'AssetOverview',
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    imageUrl: undefined
  }),
  created() {
    this.imageUrl = this.asset.imageUrl || require('@/assets/img-not-found.png')
  },
  methods: {
    like() {
      likeAsset(this.asset.id).then(asset => {
        this.$announcer.polite(`You liked '${asset.title}'`)
      })
    }
  }
}
</script>
