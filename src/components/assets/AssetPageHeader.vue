<template>
  <div class="align-content-center d-flex justify-space-between pt-2 w-100">
    <h2 id="asset-title" class="text-break mr-2">{{ asset.title }}</h2>
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
      <div v-if="canEditAsset && asset.assetType === 'link'" class="mr-2">
        <v-tooltip bottom>
          <template #activator="{on, attrs}">
            <v-btn
              id="refresh-asset-preview-btn"
              class="text-no-wrap"
              :disabled="asset.previewStatus === 'pending'"
              v-bind="attrs"
              v-on="on"
              @click="refreshPreview"
              @keypress.enter="refreshPreview"
            >
              <font-awesome-icon class="mr-2" icon="redo" />
              <span class="sr-only">Preview image last generated at {{ previewGeneratedAt | moment('lll') }}. Click to update.</span>
            </v-btn>
          </template>
          <span>Preview image last generated at {{ previewGeneratedAt | moment('lll') }}. Click to update.</span>
        </v-tooltip>
      </div>
      <div v-if="canRemixAsset" class="mr-2">
        <v-btn
          id="remix-asset-whiteboard-btn"
          @click="remix"
          @keypress.enter.prevent="remix"
        >
          <font-awesome-icon class="mr-2" icon="refresh" />
          Remix
        </v-btn>
      </div>
      <div v-if="downloadUrl" class="mr-2">
        <v-btn id="download-asset-btn" @click="downloadAsset" @keypress.enter.prevent="downloadAsset">
          <font-awesome-icon class="mr-2" icon="download" />
          Download
        </v-btn>
      </div>
      <div v-if="canDeleteAsset">
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
              <div class="d-flex pa-2">
                <div class="mr-2">
                  <v-btn
                    id="confirm-delete-btn"
                    color="primary"
                    @click="deleteConfirmed"
                    @keypress.enter="deleteConfirmed"
                  >
                    Confirm
                  </v-btn>
                </div>
                <div>
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
import {remixWhiteboard} from '@/api/whiteboards'

export default {
  name: 'AssetPageHeader',
  mixins: [Utils],
  props: {
    asset: {
      required: true,
      type: Object
    },
    refreshPreview: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    canDeleteAsset: false,
    canEditAsset: false,
    canRemixAsset: false,
    dialogConfirmDelete: undefined,
    downloadUrl: undefined
  }),
  computed: {
    previewGeneratedAt: function () {
      if (this.asset.assetType !== 'link') {
        return null
      }
      return this.$_.get(this.asset, 'previewMetadata.updatedAt') || this.asset.createdAt
    }
  },
  created() {
    if (this.asset.assetType === 'file') {
      this.downloadUrl = `${this.$config.apiBaseUrl}/api/asset/${this.asset.id}/download`
    }
    const isTeacherOrAdmin = this.$currentUser.isAdmin || this.$currentUser.isTeaching
    const isAssetOwner = this.$_.find(this.asset.users, {'id': this.$currentUser.id})
    this.canEditAsset = isTeacherOrAdmin || isAssetOwner
    this.canDeleteAsset = isTeacherOrAdmin || (isAssetOwner && !this.asset.likes && !this.asset.commentCount)
    this.canRemixAsset = this.asset.assetType === 'whiteboard'
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
    downloadAsset() {
      window.location.href = this.downloadUrl
    },
    edit() {
      this.$announcer.polite(`Edit asset ${this.asset.title}`)
      this.go(`/asset/${this.asset.id}/edit`)
    },
    remix() {
      remixWhiteboard(this.asset.id).then(whiteboard => {
        this.$announcer.polite(`Whiteboard ${whiteboard.title} is ready.`)
      })
    }
  }
}
</script>
