<template>
  <div class="align-content-center d-flex justify-space-between pt-2 w-100">
    <h2 id="asset.title">{{ asset.title }}</h2>
    <div class="d-flex align-content-end">
      <div v-if="canEditAsset" class="mr-2">
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
      <div v-if="downloadUrl" class="mr-2">
        <v-btn id="download-asset-btn" :href="downloadUrl">
          <font-awesome-icon class="mr-2" icon="download" />
          Download
        </v-btn>
      </div>
      <div v-if="canEditAsset">
        <v-dialog v-model="dialogConfirmDelete" width="500">
          <template #activator="{}">
            <v-btn
              id="delete-asset-btn"
              class="mr-3"
              @click="confirmDelete"
              @keypress.enter="confirmDelete"
            >
              <font-awesome-icon class="mr-2" icon="trash" />
              Delete
            </v-btn>
          </template>
          <v-card>
            <v-card-title id="delete-dialog-title" tabindex="-1">Delete Asset?</v-card-title>
            <v-card-text class="pt-3">
              Are you sure you want to delete <span class="font-weight-bold text-no-wrap">{{ asset.title }}</span>?
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <div class="d-flex flex-row-reverse pa-2">
                <div>
                  <v-btn
                    id="confirm-delete-btn"
                    color="primary"
                    @click="deleteConfirmed"
                    @keypress.enter="deleteConfirmed"
                  >
                    Confirm
                  </v-btn>
                </div>
                <div class="mr-2">
                  <v-btn
                    id="cancel-delete-btn"
                    @click="cancelDelete"
                    @keypress.enter="cancelDelete"
                  >
                    Cancel
                  </v-btn>
                </div>
              </div>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import {deleteAsset} from '@/api/assets'

export default {
  name: 'AssetPageHeader',
  mixins: [Utils],
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    canEditAsset: false,
    dialogConfirmDelete: undefined,
    downloadUrl: undefined
  }),
  created() {
    if (this.asset.assetType === 'file') {
      this.downloadUrl = `${this.$config.apiBaseUrl}/api/asset/${this.asset.id}/download`
    }
    this.canEditAsset = this.$currentUser.isAdmin || this.$currentUser.isTeaching || this.$_.find(this.asset.users, {'id': this.$currentUser.id})
  },
  methods: {
    cancelDelete() {
      this.dialogConfirmDelete = false
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick('asset-title')
    },
    confirmDelete() {
      this.dialogConfirmDelete = true
      this.$announcer.polite('Confirm delete')
      this.$putFocusNextTick('delete-dialog-title')
    },
    deleteConfirmed() {
      this.dialogConfirmDelete = false
      deleteAsset(this.asset.id).then(() => {
        this.$announcer.polite('Deleted')
        this.go('/assets', {m: `Asset '${this.asset.title}' deleted.`})
      })
    },
    edit() {
      this.$announcer.polite(`Edit asset ${this.asset.title}`)
      this.go(`/asset/${this.asset.id}/edit`)
    }
  }
}
</script>

<style scoped>

</style>