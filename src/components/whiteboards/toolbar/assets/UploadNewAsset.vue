<template>
  <v-dialog
    v-model="dialog"
    :close-on-content-click="false"
    width="800"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-upload-new-asset"
        :color="mode === 'upload' ? 'white' : 'primary'"
        icon
        title="Upload a new asset"
        value="upload"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Upload a new asset</span>
        <font-awesome-icon
          :color="{'white': mode === 'upload'}"
          icon="upload"
          size="lg"
        />
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pt-8">
        <div class="pb-4">
          <h2>Upload a File</h2>
          <div class="pt-2 subtitle-1">
            The uploaded file will be used to create a new asset.
            Next, the new asset will be added to this whiteboard.
          </div>
        </div>
        <div
          v-if="!uploading && !file"
          v-cloak
          id="drop-file-to-upload"
          class="file-upload-box"
          @drop.prevent="addFile"
          @dragover.prevent
        >
          <Alert
            v-if="alert"
            id="asset-library-file-upload"
            class="my-2"
            :messages="[alert]"
            type="error"
            width="auto"
          />
          <div class="file-upload-box-icon"><font-awesome-icon icon="cloud-upload-alt" /></div>
          <div class="file-upload-box-text">Drop file to upload</div>
          <div class="file-upload-box-text">or</div>
          <v-btn
            id="browse-files-btn"
            elevation="1"
            @click="browseFiles"
          >
            Browse
          </v-btn>
          <input
            ref="browseFileInput"
            class="d-none"
            type="file"
            @change="onFileBrowserChange"
          >
        </div>
        <div
          v-if="uploading"
          class="file-upload-box"
        >
          <div class="file-upload-box-icon"><font-awesome-icon icon="spinner" spin /></div>
          <div class="file-upload-box-text">Uploading...</div>
        </div>
        <v-form v-if="!uploading && file" v-model="fileAssetValid" @submit="upload">
          <v-container class="mt-2" fluid>
            <v-row>
              <v-col class="pt-5 text-right" cols="2">
                <label for="asset-title-input">
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
                  id="asset-title-input"
                  v-model="title"
                  hide-details
                  label="Enter a title"
                  maxlength="255"
                  outlined
                  required
                  @keydown.enter="upload"
                />
                <div class="pl-1">
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
            <v-row v-if="categories.length">
              <v-col class="pt-5 text-right" cols="2">
                <label for="asset-category">Category</label>
              </v-col>
              <v-col cols="10">
                <AccessibleSelect
                  id-prefix="asset-category"
                  hide-details
                  :items="categories"
                  item-text="title"
                  item-value="id"
                  label="What assignment or topic is this related to"
                  :value="categoryId"
                  @input="c => (categoryId = c)"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col class="pt-5 text-right" cols="2">
                <label for="asset-description-textarea">Description</label>
              </v-col>
              <v-col cols="10">
                <div class="d-flex flex-column flex-column-reverse">
                  <div class="caption">Add some more context to your file. You can use plain text or #keywords</div>
                  <div>
                    <v-textarea
                      id="asset-description-textarea"
                      v-model="description"
                      hide-details
                      outlined
                    />
                  </div>
                </div>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2"></v-col>
              <v-col cols="10">
                <v-checkbox
                  :id="`asset-visible-checkbox`"
                  v-model="visible"
                  hide-details
                >
                  <template #label>
                    Also add this file to Asset Library
                  </template>
                </v-checkbox>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="d-flex justify-end pt-5" cols="12">
                <div class="pr-2">
                  <v-btn
                    id="upload-file-btn"
                    color="primary"
                    :disabled="!file || !fileAssetValid"
                    elevation="1"
                    @click="upload"
                  >
                    Upload file
                  </v-btn>
                </div>
                <div>
                  <v-btn id="upload-file-cancel-btn" elevation="1" @click="go('/assets')">Cancel</v-btn>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Alert from '@/components/util/Alert'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import {createFileAsset} from '@/api/assets'

export default {
  name: 'UploadNewAsset',
  components: {AccessibleSelect, Alert},
  mixins: [Context, Utils, Whiteboarding],
  data() {
    return {
      alert: undefined,
      categoryId: undefined,
      description: undefined,
      dialog: false,
      file: undefined,
      fileAssetValid: false,
      isSaving: false,
      title: '',
      uploading: false,
      visible: true
    }
  },
  methods: {
    addFile(e) {
      this.selectFile(e.dataTransfer.files)
    },
    browseFiles() {
      this.$refs.browseFileInput.click()
    },
    onFileBrowserChange(e) {
      this.selectFile(e.target.files)
    },
    selectFile(files) {
      this.alert = null
      if (this.$_.size(files) > 0) {
        if (files[0].size > 10485760) {
          this.alert = `The file "${files[0].name}" is too large. Files can be maximum 10MB in size.`
        } else {
          this.file = files[0]
          this.title = this.file.name
          this.$announcer.polite(`${this.file} added`)
        }
      }
    },
    upload() {
      this.uploading = true
      if (this.file && this.title) {
        createFileAsset(
          this.categoryId,
          this.description,
          this.title,
          this.file,
          this.visible
        ).then(asset => {
          this.addAsset(asset).then(() => {
            this.$announcer.polite('File uploaded. Asset created.')
            this.dialog = false
            this.isSaving = false
            this.uploading = false
          })
        })
      }
    }
  }
}
</script>
