<template>
  <div class="preview-outer">
    <div v-if="previewStatus === 'done'" class="preview">
      <div v-if="asset.assetType === 'file' && !asset.pdfUrl && !videoUrl && asset.imageUrl">
        <v-img
          id="asset-preview"
          :alt="`Image preview of ${asset.title}`"
          :contain="contain"
          :max-height="maxHeight"
          :src="asset.imageUrl"
          @error="imgError"
        />
      </div>
      <div v-if="asset.assetType === 'file' && asset.pdfUrl">
        <iframe
          id="asset-preview"
          allowfullscreen=""
          allowscriptaccess="always"
          class="preview-document"
          frameborder="0"
          height="800"
          mozallowfullscreen=""
          scrolling="no"
          :src="embedUrl"
          webkitallowfullscreen=""
          width="100%"
        />
      </div>
      <div v-if="asset.assetType === 'file' && !asset.pdfUrl && videoUrl" class="preview-video-wrapper">
        <video
          id="asset-preview"
          :alt="asset.title"
          class="preview-video"
          controls
          :height="height"
          :poster="asset.image_url"
          :title="asset.title"
          :width="width"
        >
          <source :src="videoUrl" type="video/mp4">
        </video>
      </div>
      <div v-if="asset.assetType === 'link' && isEmbeddable && !asset.previewMetadata.youtubeId">
        <iframe
          id="asset-preview"
          frameborder="0"
          height="800"
          :src="embedUrl"
          width="100%"
        />
      </div>
      <div v-if="asset.assetType === 'link' && isEmbeddable && asset.previewMetadata.youtubeId">
        <iframe
          id="asset-preview"
          allowfullscreen=""
          allowscriptaccess="always"
          frameborder="0"
          height="800"
          mozallowfullscreen=""
          scrolling="no"
          :src="embedUrl"
          webkitallowfullscreen=""
          width="100%"
        />
      </div>
      <div v-if="asset.assetType === 'link' && !isEmbeddable && asset.imageUrl">
        <v-img
          id="asset-preview"
          :alt="`Image preview of ${asset.title}`"
          :contain="contain"
          :max-height="maxHeight"
          :src="asset.imageUrl"
          :title="asset.title"
          @error="imgError"
        />
      </div>
      <div v-if="asset.assetType === 'whiteboard'" class="whiteboard-preview">
        <AssetTypeWhiteboard :asset="asset" :max-height="maxHeight" />
      </div>
    </div>
    <div
      v-if="previewStatus === 'pending'"
      class="preview-message"
    >
      <font-awesome-icon icon="spinner" spin />
      Preparing a preview...
    </div>
    <div
      v-if="previewStatus === 'unsupported' || previewStatus === 'error'"
      class="preview-message"
    >
      No preview available.
    </div>
  </div>
</template>

<script>
import AssetTypeWhiteboard from '@/components/assets/AssetTypeWhiteboard'

export default {
  name: 'AssetPreview',
  components: {AssetTypeWhiteboard},
  props: {
    asset: {
      required: true,
      type: Object
    },
    contain: {
      required: false,
      type: Boolean
    },
    maxHeight: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  data: () => ({
    embedUrl: undefined,
    height: undefined,
    isEmbeddable: undefined,
    imageUrl: undefined,
    videoUrl: undefined,
    width: undefined
  }),
  computed: {
    previewStatus() {
      return this.asset.previewStatus
    }
  },
  created() {
    this.decorateAssetFeed()
  },
  watch: {
    previewStatus() {
      this.decorateAssetFeed()
    }
  },
  methods: {
    decorateAssetFeed() {
      if (this.previewStatus === 'done') {
        if (this.asset.assetType === 'file') {
          if (this.asset.pdfUrl) {
            this.embedUrl = this.$config.staticPath + '/viewer/viewer.html?file=' + encodeURIComponent(this.asset.pdfUrl)
          } else if (this.$_.startsWith(this.asset.mime, 'video') && this.asset.imageUrl && this.asset.downloadUrl) {
            this.videoUrl = this.getVideoUrl(this.asset)
            this.height = this.asset.previewMetadata.image_height
            this.width = this.asset.previewMetadata.image_width
          }
        } else if (this.asset.assetType === 'link') {
          var currentProtocol = document.location.protocol
          if (this.asset.previewMetadata.youtubeId) {
            this.isEmbeddable = true
            this.embedUrl = currentProtocol + '//www.youtube.com/embed/' + this.asset.previewMetadata.youtubeId + '?autoplay=false'
          } else {
            var alternateEmbedUrl = null
            if (currentProtocol === 'http:') {
              this.isEmbeddable = this.asset.previewMetadata.httpEmbeddable
              alternateEmbedUrl = this.asset.previewMetadata.httpEmbedUrl
            } else if (currentProtocol === 'https:') {
              this.isEmbeddable = this.asset.previewMetadata.httpsEmbeddable
              alternateEmbedUrl = this.asset.previewMetadata.httpsEmbedUrl
            }
            this.embedUrl = (alternateEmbedUrl || this.asset.url).replace(/^https?:/, currentProtocol)
          }
        }
      }
    },
    getVideoUrl(asset) {
      return asset.previewMetadata.converted_video || `${this.$config.apiBaseUrl}/api/asset/${asset.id}/download`
    },
    imgError() {
      this.imageUrl = require('@/assets/img-not-found.png')
    }
  }
}
</script>

<style scoped>
.preview iframe {
  background-color: #FFF;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  width: 100%;
}

.preview .preview-document,
.whiteboard-preview {
  border-bottom: 1px solid #D3D3D3;
}

.preview .preview-document {
  height: 400px;
  width: 100%;
}

@media only screen and (min-width : 768px) {
  .preview .preview-image {
    padding: 5px;
  }

  .preview .preview-video {
    margin-top: 20px;
  }

  .preview .preview-video-wrapper {
    line-height: 0;
  }

  .preview iframe,
  .preview .preview-document,
   .whiteboard-preview {
    height: 720px;
  }
}
.preview-message {
  background-color: #FFF;
  padding: 170px 0;
}
.preview-message > i {
  color: #747474;
  font-size: 50px;
}
.preview-message p {
  font-size: 18px;
  margin: 15px 20px 0;
}
.preview-message a {
  margin-top: 15px;
}
.preview-message i.fa-spinner {
  margin-right: 5px;
}
.preview-outer {
  text-align: center;
}
</style>
