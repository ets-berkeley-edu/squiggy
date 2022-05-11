<template>
  <v-dialog
    v-model="dialog"
    :close-on-content-click="false"
    :disabled="isRemixing"
    width="500"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="remix-asset-whiteboard-btn"
        class="justify-start w-100"
        :disabled="isRemixing"
        elevation="0"
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon class="mr-2" icon="refresh" />
        Remix
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pl-8 pt-8">
        <v-container v-if="!whiteboard" fluid>
          <v-row>
            <v-col>
              <h2 id="modal-header" class="pl-3">Remixing...</h2>
            </v-col>
          </v-row>
          <v-row justify="center pb-12">
            <v-col class="text-center">
              <v-progress-circular
                class="spinner"
                :indeterminate="true"
                rotate="5"
                size="32"
                width="4"
                color="light-blue"
              />
            </v-col>
          </v-row>
        </v-container>
        <v-container v-if="whiteboard" fluid>
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
                A new whiteboard has been created.
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
                <h2 id="whiteboard-title">{{ whiteboard.title }}</h2>
                <div class="pl-1">
                  <a
                    id="link-to-whiteboard"
                    :href="$router.resolve({path: `/whiteboard/${whiteboard.id}`}).href"
                    target="_blank"
                    aria-label="Open whiteboard in new window"
                  >
                    <font-awesome-icon icon="arrow-up-right-from-square" class="pl-1" />
                  </a>
                </div>
              </div>
              <div class="d-flex">
                <div class="pr-2 pt-1">Created by</div>
                <OxfordJoin v-slot="{item}" :items="whiteboard.users">
                  <div class="align-center d-flex pr-1">
                    <Avatar :user="item" />
                    <UserLink :cross-tool-link="true" :user="item" />
                  </div>
                </OxfordJoin>
                <div class="pt-1">
                  on {{ whiteboard.createdAt | moment('LL') }}
                </div>
              </div>
            </v-col>
          </v-row>
          <v-row v-if="whiteboard.description" class="pt-2" no-gutters>
            <v-col id="whiteboard-description">
              <h3 class="sr-only">Description XXX</h3>
              {{ whiteboard.description }}
            </v-col>
          </v-row>
          <v-row v-if="whiteboard.categories.length">
            <v-col>
              <h3>{{ whiteboard.categories.length === 1 ? 'Category' : 'Categories' }}</h3>
              <div>
                {{ oxfordJoin($_.map(whiteboard.categories, 'title')) }}
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
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import OxfordJoin from '@/components/util/OxfordJoin'
import UserLink from '@/components/util/UserLink'
import Utils from '@/mixins/Utils'
import {remixWhiteboard} from '@/api/whiteboards'

export default {
  name: 'RemixAsset',
  mixins: [Utils],
  components: {Avatar, OxfordJoin, UserLink},
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    dialog: false,
    isRemixing: false,
    whiteboard: undefined
  }),
  watch: {
    dialog(flag) {
      if (!this.isRemixing) {
        if (flag) {
          this.remix()
        } else {
          this.whiteboard = undefined
        }
      }
    }
  },
  methods: {
    onClickClose() {
      this.dialog = false
      this.$announcer.polite('Closed')
    },
    remix() {
      this.$announcer.polite('Begin the remix...')
      this.isRemixing = true
      remixWhiteboard(this.asset.id).then(whiteboard => {
        this.whiteboard = whiteboard
        this.$announcer.polite(`Whiteboard ${this.whiteboard.title} is ready.`)
        this.isRemixing = false
      })
    }
  }
}
</script>
