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
        <h2 id="asset-title">{{ asset.title }}</h2>
        <div class="pb-3 pt-2">
          <a
            id="link-to-asset"
            class="hover-link"
            :href="`${assetLibraryUrl}#suitec_assetId=${asset.id}`"
            target="_blank"
          >
            Open asset in new window
            <font-awesome-icon icon="arrow-up-right-from-square" class="pr-1" />
          </a>
        </div>
        <div v-if="asset.users.length === 1">
          <div class="align-center d-flex">
            <div class="pr-2">Owned by</div>
            <div class="pr-2">
              <Avatar :user="asset.users[0]" />
            </div>
            <div>
              <a
                :id="`owned-by-user-${asset.users[0].id}-href`"
                class="hover-link"
                :href="`${assetLibraryUrl}#suitec_userId=${asset.users[0].id}`"
                target="_parent"
              >
                <font-awesome-icon
                  v-if="asset.users[0].isAdmin || asset.users[0].isTeaching"
                  :id="`user-${asset.users[0].id}-graduation-cap`"
                  icon="graduation-cap"
                  class="ml-2"
                />
                {{ asset.users[0].canvasFullName }}
              </a>
            </div>
          </div>
        </div>
        <div v-if="asset.users.length > 1">
          <h3 class="mb-1 subtitle-1">Owned by:</h3>
          <div v-for="user in asset.users" :key="user.id" class="pb-1">
            <div class="align-center d-flex">
              <div class="pl-2">
                <Avatar :user="user" />
              </div>
              <div class="pl-2">
                <a
                  :id="`owned-by-user-${user.id}-href`"
                  class="hover-link"
                  :href="`${assetLibraryUrl}#suitec_orderBy=recent&suitec_userId=${user.id}`"
                  target="_parent"
                >
                  <font-awesome-icon
                    v-if="user.isAdmin || user.isTeaching"
                    :id="`user-${user.id}-graduation-cap`"
                    icon="graduation-cap"
                    class="ml-2"
                  />
                  {{ user.canvasFullName }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="asset.description" class="pt-2" no-gutters>
      <v-col id="asset-description" class="pb-2 pt-3">
        <h3 class="">Description</h3>
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
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ExportSummary',
  mixins: [Utils, Whiteboarding],
  components: {Avatar},
  props: {
    asset: {
      required: true,
      type: Object
    },
    onClickClose: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    assetLibraryUrl: undefined
  }),
  created() {
    this.assetLibraryUrl = this.$currentUser.course.assetLibraryUrl
  }
}
</script>
