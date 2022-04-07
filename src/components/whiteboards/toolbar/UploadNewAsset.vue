<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-upload-new-asset"
        :disabled="disableAll"
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon icon="laptop" />
        <span class="pl-2">Upload New</span>
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pt-8">
        <h2>Upload a File</h2>
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
              <v-col cols="6">
                <v-text-field
                  id="asset-title-input"
                  v-model="title"
                  label="Enter a title"
                  outlined
                  required
                  :rules="titleRules"
                  @keydown.enter="upload"
                />
              </v-col>
            </v-row>
            <v-row v-if="categories.length">
              <v-col class="pt-5 text-right" cols="2">
                <label for="asset-category">Category</label>
              </v-col>
              <v-col cols="6">
                <AccessibleSelect
                  id-prefix="asset-category"
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
              <v-col cols="6">
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
            <v-row>
              <v-col class="text-right" cols="8">
                <div class="d-flex">
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
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
    </v-card>
  </v-menu>
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
      file: undefined,
      fileAssetValid: false,
      isSaving: false,
      menu: false,
      title: '',
      titleRules: [
        v => !!this.$_.trim(v) || 'Please enter a title',
        v => (!v || v.length <= 255) || 'Title must be 255 characters or less',
      ],
      uploading: false
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
        createFileAsset(this.categoryId, this.description, this.title, this.file).then(asset => {
          this.addAsset(asset).then(() => {
            this.$announcer.polite('File uploaded. Asset created.')
            this.menu = false
            this.isSaving = false
          })
        })
      }
    }
  }
}
</script>
