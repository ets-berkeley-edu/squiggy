<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-row justify="space-between">
          <v-col v-for="user in asset.users" :key="user.id">
            <div class="align-center d-flex">
              <div class="pr-1">
                by
              </div>
              <div class="pr-1">
                <Avatar :user="user" />
              </div>
              <div>
                <span :id="`by-user-${user.id}`">{{ user.canvasFullName }}</span> on {{ asset.createdAt | moment('LL') }}
              </div>
            </div>
          </v-col>
          <v-col>
            <v-row align="center" justify="end">
              <div class="mr-3">
                <v-btn
                  id="like-asset-btn"
                  icon
                  class="like-asset-btn"
                  :class="{'like-asset-btn-liked': liked}"
                  @click="toggleLike"
                  @keypress.enter.prevent="toggleLike"
                >
                  <font-awesome-icon icon="thumbs-up" />
                  <span id="asset-like-count" class="ml-1">{{ likeCount }}</span>
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
      <v-col id="asset-description">
        <h3 class="sr-only">Description</h3>
        {{ asset.description }}
      </v-col>
    </v-row>
    <v-row>
      <v-col
        class="font-weight-bold text-no-wrap"
        lg="1"
        md="1"
        sm="2"
      >
        Source:
      </v-col>
      <v-col v-if="sourceUrl">
        <a :href="sourceUrl" target="_blank">{{ sourceUrl }}</a>
      </v-col>
      <v-col v-if="!sourceUrl">&mdash;</v-col>
    </v-row>
    <v-row justify="start">
      <v-col
        class="font-weight-bold text-no-wrap"
        lg="1"
        md="1"
        sm="2"
      >
        {{ asset.categories.length === 1 ? 'Category' : 'Categories' }}:
      </v-col>
      <v-col>
        <div v-if="asset.categories.length">
          <OxfordJoin v-slot="{item}" :items="asset.categories">
            <router-link
              :id="`link-to-assets-of-category-${item.id}`"
              :aria-label="`View assets, filtered by category ${item.name}`"
              :to="`/assets?categoryId=${item.id}`"
            >
              {{ item.name }}
            </router-link>
          </OxfordJoin>
          {{ asset.categories.length ? oxfordJoin($_.map(asset.categories, 'title')) : '' }}
        </div>
        <div v-if="!asset.categories.length">
          &mdash;
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import OxfordJoin from '@/components/util/OxfordJoin'
import Utils from '@/mixins/Utils'
import {likeAsset, removeLikeAsset} from '@/api/assets'

export default {
  name: 'AssetOverview',
  components: {Avatar, OxfordJoin},
  mixins: [Utils],
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    imageUrl: undefined,
    likeCount: undefined,
    liked: undefined,
    sourceUrl: undefined
  }),
  created() {
    this.imageUrl = this.asset.imageUrl || require('@/assets/img-not-found.png')
    this.likeCount = this.asset.likes
    this.liked = this.asset.liked
    this.sourceUrl = this.asset.source || this.asset.url
  },
  methods: {
    toggleLike() {
      if (this.liked) {
        removeLikeAsset(this.asset.id).then(data => {
          this.likeCount = data.likes
          this.liked = data.liked
          this.$announcer.polite(`You removed your like from '${data.title}'`)
        })
      } else {
        likeAsset(this.asset.id).then(data => {
          this.likeCount = data.likes
          this.liked = data.liked
          this.$announcer.polite(`You liked '${data.title}'`)
        })
      }
    }
  }
}
</script>

<style scoped>
.like-asset-btn:hover {
  color: #719fdd;
}

.like-asset-btn-liked {
  color: #4172b4 !important;
}
</style>
