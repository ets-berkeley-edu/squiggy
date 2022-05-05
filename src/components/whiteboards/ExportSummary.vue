<template>
  <v-container v-if="asset.id" fluid>
    <v-row>
      <v-col>
        <div
          aria-live="polite"
          class="align-center d-flex"
          role="alert"
        >
          <font-awesome-icon
            class="primary--text"
            icon="circle-check"
            size="2x"
          />
          <h2 id="modal-header" class="pl-3">
            Congratulations!
          </h2>
        </div>
        <div class="pt-2">
          Your newly created asset is summarized below.
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-divider />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <div class="d-flex pb-4">
          <h2 id="asset-title">{{ asset.title }}</h2>
          <div class="pl-1">
            <a
              id="link-to-asset"
              :href="`${$currentUser.course.assetLibraryUrl}#suitec_assetId=${asset.id}`"
              target="_blank"
              aria-label="Open asset in new window"
            >
              <font-awesome-icon icon="arrow-up-right-from-square" class="pl-1" />
            </a>
          </div>
        </div>
        <div class="d-flex">
          <div class="pr-2 pt-1">Created by</div>
          <OxfordJoin v-slot="{item}" :items="asset.users">
            <div class="align-center d-flex pr-1">
              <Avatar :user="item" />
              <UserLink :cross-tool-link="true" :user="item" />
            </div>
          </OxfordJoin>
          <div class="pt-1">
            on {{ asset.createdAt | moment('LL') }}
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="asset.description" class="pt-2" no-gutters>
      <v-col id="asset-description">
        <h3 class="sr-only">Description</h3>
        {{ asset.description }}
      </v-col>
    </v-row>
    <v-row v-if="asset.categories.length">
      <v-col>
        <h3>{{ asset.categories.length === 1 ? 'Category' : 'Categories' }}</h3>
        <div>
          {{ oxfordJoin($_.map(asset.categories, 'title')) }}
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col class="d-flex justify-end pt-5">
        <v-btn
          id="close-btn"
          color="primary"
          @click="onClickClose"
          @keypress.enter="onClickClose"
        >
          Close
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import OxfordJoin from '@/components/util/OxfordJoin'
import UserLink from '@/components/util/UserLink'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ExportSummary',
  mixins: [Utils, Whiteboarding],
  components: {Avatar, OxfordJoin, UserLink},
  props: {
    asset: {
      required: true,
      type: Object
    },
    onClickClose: {
      required: true,
      type: Function
    }
  }
}
</script>
