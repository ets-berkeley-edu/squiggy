<template>
  <v-container class="mt-3" fluid>
    <v-row class="mt-3" no-gutters>
      <v-col
        class="font-weight-bold pr-2 text-no-wrap text-right"
        lg="1"
        md="1"
        sm="2"
      >
        Created:
      </v-col>
      <v-col>
        {{ asset.createdAt | moment('LL') }}
      </v-col>
      <v-col class="text-right">
        <v-container class="py-0" fluid>
          <v-row align="center" justify="end" no-gutters>
            <div v-if="canLikeAsset" class="mr-5">
              <v-btn
                id="like-asset-btn"
                icon
                class="like-asset-btn pt-0 mt-0"
                :class="{'like-asset-btn-liked': liked}"
                @click="toggleLike"
                @keypress.enter.prevent="toggleLike"
              >
                <font-awesome-icon icon="thumbs-up" />
                <span id="asset-like-count" class="ml-1">{{ likeCount }}</span>
                <span class="sr-only">{{ likeCount === 1 ? 'like' : 'likes' }}</span>
              </v-btn>
            </div>
            <div v-if="!canLikeAsset" class="mr-5">
              <font-awesome-icon icon="thumbs-up" />
              <span id="asset-like-count" class="ml-1">{{ likeCount }}</span>
              <span class="sr-only">{{ likeCount === 1 ? 'like' : 'likes' }}</span>
            </div>
            <div class="mr-5">
              <font-awesome-icon icon="eye" />
              <span id="asset-view-count" class="ml-1">{{ asset.views }}</span>
              <span class="sr-only">{{ asset.views === 1 ? 'view' : 'views' }}</span>
            </div>
            <div class="mr-3">
              <font-awesome-icon icon="comment" />
              <span id="asset-comment-count" class="ml-1">{{ asset.commentCount }}</span>
              <span class="sr-only">{{ asset.commentCount === 1 ? 'comment' : 'comments' }}</span>
            </div>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <v-row class="mt-3" no-gutters>
      <v-col
        class="font-weight-bold pr-2 pt-1 text-no-wrap text-right"
        lg="1"
        md="1"
        sm="2"
      >
        Owned by:
      </v-col>
      <v-col>
        <div v-if="asset.users.length === 1">
          <div class="align-center d-flex">
            <div>
              <Avatar :user="asset.users[0]" />
            </div>
            <div class="pl-1">
              <UserLink :user="asset.users[0]" />
            </div>
          </div>
        </div>
        <div v-if="asset.users.length > 1">
          <div v-for="user in asset.users" :key="user.id" class="pb-1">
            <div class="align-center d-flex">
              <div>
                <Avatar :user="user" />
              </div>
              <div class="pl-2">
                <UserLink :user="user" />
              </div>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row class="mt-3" no-gutters>
      <v-col
        align-self="start"
        class="font-weight-bold pr-2 text-no-wrap text-right"
        lg="1"
        md="1"
        sm="2"
      >
        Description:
      </v-col>
      <v-col id="asset-description" align-self="center">
        {{ asset.description }} XXX
      </v-col>
    </v-row>
    <v-row v-if="!['file', 'whiteboard'].includes(asset.assetType)" class="mt-3" no-gutters>
      <v-col
        class="font-weight-bold pr-2 text-no-wrap text-right"
        lg="1"
        md="1"
        sm="2"
      >
        Source:
      </v-col>
      <v-col v-if="sourceUrl">
        <a :href="sourceUrl" target="_blank">
          <span class="sr-only">Open in new window:</span>
          {{ sourceUrl }}
        </a>
      </v-col>
      <v-col v-if="!sourceUrl">
        &mdash;
        <span class="sr-only">none</span>
      </v-col>
    </v-row>
    <v-row v-if="$_.size(usedInAssets)" class="mt-3" no-gutters>
      <v-col
        class="font-weight-bold pr-2 text-no-wrap text-right"
        lg="1"
        md="1"
        sm="2"
      >
        Used in:
      </v-col>
      <v-col>
        <div
          v-for="(usedInAsset, index) in usedInAssets"
          :key="index"
          :class="{'pt-1': index > 0}"
        >
          <router-link
            :id="`asset-used-in-${usedInAsset.id}`"
            :to="`/asset/${usedInAsset.id}`"
          >
            {{ usedInAsset.title }}
          </router-link>
        </div>
      </v-col>
    </v-row>
    <v-row class="mt-3" no-gutters>
      <v-col
        class="font-weight-bold pr-2 text-no-wrap text-right"
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
              :aria-label="`View assets, filtered by category ${item.title}`"
              :to="`/assets?categoryId=${item.id}`"
              class="hover-link"
            >
              {{ item.title }}
            </router-link>
          </OxfordJoin>
        </div>
        <div v-if="!asset.categories.length">
          &mdash;
          <span class="sr-only">none</span>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import AssetsSearch from '@/mixins/AssetsSearch'
import Avatar from '@/components/user/Avatar'
import OxfordJoin from '@/components/util/OxfordJoin'
import UserLink from '@/components/util/UserLink'
import Utils from '@/mixins/Utils'
import {likeAsset, removeLikeAsset} from '@/api/assets'

export default {
  name: 'AssetOverview',
  components: {Avatar, OxfordJoin, UserLink},
  mixins: [AssetsSearch, Utils],
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    canLikeAsset: false,
    imageUrl: undefined,
    likeCount: undefined,
    liked: undefined,
    sourceUrl: undefined,
    usedInAssets: undefined
  }),
  created() {
    this.canLikeAsset = !(this.$_.find(this.asset.users, {id: this.$currentUser.id}))
    this.imageUrl = this.asset.imageUrl || require('@/assets/img-not-found.png')
    this.likeCount = this.asset.likes
    this.liked = this.asset.liked
    this.sourceUrl = this.asset.source || this.asset.url
    this.usedInAssets = this.getUsedInAssets()
  },
  methods: {
    getUsedInAssets() {
      const assets = []
      const showAll = this.$currentUser.isAdmin || this.$currentUser.isTeaching
      this.$_.each(this.asset.usedInAssets, usedInAsset => {
        if (usedInAsset.id !== this.asset.id && (showAll || usedInAsset.visible)) {
          assets.push(usedInAsset)
        }
      })
      return assets
    },
    toggleLike() {
      if (this.liked) {
        removeLikeAsset(this.asset.id).then(data => {
          this.likeCount = data.likes
          this.liked = data.liked
          this.updateAssetStore(data)
          this.$announcer.polite(`You removed your like from '${data.title}'`)
        })
      } else {
        likeAsset(this.asset.id).then(data => {
          this.likeCount = data.likes
          this.liked = data.liked
          this.updateAssetStore(data)
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
