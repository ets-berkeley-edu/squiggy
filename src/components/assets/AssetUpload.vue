<template>
  <div>
    <h2>Upload a file</h2>
    <div
      v-cloak
      id="drop-file-to-upload"
      style="height: 400px; background-color: #378dc5"
      @drop.prevent="addFile"
      @dragover.prevent
    >
      <h2>Files to Upload (Drag them over)</h2>
      <v-btn class="w-50" :disabled="!file" @click="upload">Upload</v-btn>
    </div>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import {uploadFile} from '@/api/assets'

export default {
  name: 'UploadAsset',
  mixins: [Utils],
  data: () => ({
    file: undefined
  }),
  methods: {
    addFile(e) {
      const files = e.dataTransfer.files
      if (this.$_.size(files) > 0) {
        this.file = files[0]
      }
    },
    removeFile(file){
      this.files = this.file.filter(f => f !== file)
    },
    upload() {
      uploadFile(this.file).then(asset => {
        this.$announcer.polite('File uploaded and asset created.')
        this.go(`/asset/${asset.id}`)
      })
    }
  }
}
</script>
