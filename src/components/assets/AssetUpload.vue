<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary anchor="assets-container" />
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
    <v-form v-if="!uploading && file" @submit="upload">
      <v-container class="mt-2" fluid>
        <v-row>
          <v-col class="pt-7 text-right" cols="2">
            Title
          </v-col>
          <v-col cols="6">
            <v-text-field
              id="asset-title-input"
              v-model="title"
              label="Enter a title"
              maxlength="255"
              outlined
              @keydown.enter="submit"
            />
          </v-col>
        </v-row>
        <v-row v-if="categories.length">
          <v-col class="pt-7 text-right" cols="2">
            Category
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
          <v-col class="pt-7 text-right" cols="2">
            Description
          </v-col>
          <v-col cols="6">
            <v-textarea
              id="asset-description-textarea"
              v-model="description"
              outlined
              placeholder="Add some more context to your file. You can use plain text or #keywords"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="text-right" cols="8">
            <div class="d-flex flex-row-reverse">
              <div>
                <v-btn
                  id="upload-file-btn"
                  color="primary"
                  :disabled="disable"
                  elevation="1"
                  @click="upload"
                >
                  Upload file
                </v-btn>
              </div>
              <div class="pr-2">
                <v-btn id="upload-file-cancel-btn" elevation="1" @click="go('/assets')">Cancel</v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-form>
  </div>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Alert from '@/components/util/Alert'
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {createFileAsset} from '@/api/assets'
import {getCategories} from '@/api/categories'

export default {
  name: 'AssetUpload',
  components: {AccessibleSelect, Alert, BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    alert: undefined,
    categories: undefined,
    categoryId: undefined,
    description: undefined,
    file: undefined,
    title: undefined,
    uploading: false
  }),
  computed: {
    disable() {
      return !(this.file && this.$_.trim(this.title))
    }
  },
  created() {
    this.$loading()
    getCategories().then(data => {
      this.categories = data
      this.$ready('Upload a file')
    })
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
      createFileAsset(this.categoryId, this.description, this.title, this.file).then(() => {
        this.$announcer.polite('File uploaded. Asset created.')
        this.go('/assets')
      })
    }
  }
}
</script>

<style scoped>
.file-upload-box {
  background-color: #F7F7F7;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  display: table;
  height: 280px;
  margin-bottom: 10px;
  padding-left: 10%;
  padding-right: 10%;
  padding-top: 40px;
  text-align: center;
  width: 100%;
}
.file-upload-box-text {
  font-size: 20px;
  line-height: 24px;
  margin: 10px;
}
.file-upload-box-icon {
  color: #747474;
  font-size: 48px;
}
</style>