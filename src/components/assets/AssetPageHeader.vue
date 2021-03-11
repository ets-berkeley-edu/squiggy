<template>
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
          :disabled="disableButtons"
          @click="edit"
          @keypress.enter="edit"
        >
          <font-awesome-icon class="mr-2" icon="pencil-alt" />
          Edit Details
        </v-btn>
      </div>
      <div class="mr-2">
        <v-btn
          id="download-asset-btn"
          :disabled="disableButtons"
          :href="downloadUrl"
        >
          <font-awesome-icon class="mr-2" icon="download" />
          Download
        </v-btn>
      </div>
      <div>
        <v-dialog v-model="dialogConfirmDelete" width="500">
          <template #activator="{}">
            <v-btn
              id="delete-asset-btn"
              class="mr-3"
              :disabled="disableButtons"
              @click="confirmDelete"
              @keypress.enter="confirmDelete"
            >
              <font-awesome-icon class="mr-2" icon="trash" />
              Delete
            </v-btn>
          </template>
          <v-card>
            <v-card-title id="delete-dialog-title" tabindex="-1">Delete Asset?</v-card-title>
            <v-card-text>
              Are you sure you want to delete <span class="font-weight-bold">{{ asset.title }}</span>?
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <div class="d-flex flex-row-reverse">
                <v-btn
                  id="confirm-delete-btn"
                  color="primary"
                  :disabled="disableButtons"
                  text
                  @click="deleteConfirmed"
                >
                  Confirm
                </v-btn>
                <v-btn
                  id="cancel-delete-btn"
                  :disabled="disableButtons"
                  text
                  @click="cancelDelete"
                >
                  Cancel
                </v-btn>
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
import {deleteAsset, downloadAsset} from '@/api/assets'

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
    dialogConfirmDelete: undefined,
    disableButtons: false,
    downloadUrl: undefined
  }),
  created() {
    this.downloadUrl = `${this.$config.apiBaseUrl}/api/asset/${this.asset.id}/download`
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
    download() {
      this.$announcer.polite('Downloading')
      downloadAsset(this.asset.id).then(() => {
        this.$announcer.polite(`${this.asset.title} downloaded.`)
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