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
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon class="mr-2" icon="refresh" />
        Remix
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pt-6">
        <v-container v-if="isEditingTitle" fluid>
          <v-row>
            <v-col>
              <div
                aria-live="polite"
                class="align-center d-flex"
                role="alert"
              >
                <h2 id="modal-header">
                  Name your whiteboard
                </h2>
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-divider />
            </v-col>
          </v-row>
          <v-row>
            <v-col class="pt-5" cols="2">
              <label class="float-right" for="whiteboard-title-input">
                Title
                <font-awesome-icon
                  aria-label="Icon indicates required field"
                  class="deep-orange--text icon-denotes-required"
                  icon="asterisk"
                  size="xs"
                />
              </label>
            </v-col>
            <v-col cols="10">
              <v-text-field
                id="whiteboard-title-input"
                v-model="title"
                hide-details
                maxlength="255"
                outlined
                required
                @keydown.enter="remix"
              />
              <div class="pl-1 py-1">
                <span
                  :aria-live="title.length === 255 ? 'assertive' : null"
                  class="font-size-12"
                  :class="title.length === 255 ? 'red--text' : 'text--secondary'"
                  role="alert"
                >
                  255 character limit
                  <span v-if="title.length">({{ 255 - title.length }} remaining)</span>
                </span>
              </div>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="d-flex justify-end pt-5">
              <div class="pr-2">
                <v-btn
                  id="remix-btn"
                  color="primary"
                  :disabled="disableRemix"
                  @click="remix"
                  @keypress.enter="remix"
                >
                  <font-awesome-icon
                    v-if="isRemixing"
                    class="mr-2"
                    icon="spinner"
                    :spin="true"
                  />
                  <span v-if="isRemixing">Remixing...</span>
                  <span v-if="!isRemixing">Remix</span>
                </v-btn>
              </div>
              <div>
                <v-btn
                  id="cancel-btn"
                  text
                  @click="cancel"
                  @keypress.enter="cancel"
                >
                  Cancel
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-container>
        <v-container v-if="isDone" fluid>
          <v-row>
            <v-col>
              <div
                aria-live="polite"
                class="align-center d-flex"
                role="alert"
              >
                <font-awesome-icon
                  class="mr-2 primary--text"
                  icon="circle-check"
                  size="2x"
                />
                <h2 id="modal-header">
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
              <div class="pb-4">
                <div class="d-flex">
                  <a
                    id="link-to-whiteboard"
                    :href="$router.resolve({path: `/whiteboard/${whiteboard.id}`}).href"
                    target="_blank"
                    aria-label="Open whiteboard in new window"
                  >
                    <div class="align-center d-flex">
                      <div id="whiteboard-title" class="pr-2 text-h5">{{ whiteboard.title }}</div>
                      <div>
                        <font-awesome-icon icon="arrow-up-right-from-square" class="pl-1" />
                      </div>
                    </div>
                  </a>
                </div>
                <div>
                  <span class="text-caption">(The link above will open in a new window.)</span>
                </div>
              </div>
              <div class="d-flex">
                <div class="pr-2 pt-1">Created by</div>
                <OxfordJoin v-slot="{item}" :items="whiteboard.users">
                  <div class="align-center d-flex pr-1">
                    <Avatar :user="item" />
                    <UserLink :user="item" />
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
              <h3 class="sr-only">Description</h3>
              {{ whiteboard.description }}
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="d-flex justify-end pt-5">
              <v-btn
                id="close-btn"
                color="primary"
                @click="close"
                @keypress.enter="close"
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
    isEditingTitle: false,
    isDone: false,
    isRemixing: false,
    title: '',
    whiteboard: undefined
  }),
  watch: {
    dialog(isOpen) {
      if (!this.isRemixing) {
        if (isOpen) {
          this.promptUserForName()
        } else {
          this.title = ''
          this.whiteboard = undefined
        }
      }
    }
  },
  computed: {
    disableRemix() {
      return !this.$_.trim(this.title).length
    }
  },
  methods: {
    cancel() {
      this.close('Canceled')
    },
    close(srAlert) {
      this.dialog = this.isEditingTitle = this.isDone = false
      this.$announcer.polite(srAlert || 'Closed')
    },
    promptUserForName() {
      this.isEditingTitle = true
      this.$announcer.polite('Open form to name your whiteboard')
      this.title = this.asset.title
      this.$putFocusNextTick('modal-header')
    },
    remix() {
      if (!this.disableRemix) {
        this.$announcer.polite('Begin the remix...')
        this.isRemixing = true
        remixWhiteboard(this.asset.id, this.$_.trim(this.title)).then(whiteboard => {
          this.whiteboard = whiteboard
          this.$announcer.polite(`Whiteboard ${this.whiteboard.title} is ready.`)
          this.isEditingTitle = this.isRemixing = false
          this.isDone = true
          this.$putFocusNextTick('modal-header')
        })
      }
    }
  }
}
</script>
