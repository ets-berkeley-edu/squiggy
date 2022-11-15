<template>
  <v-img
    id="asset-preview"
    :alt="`Image preview of ${asset.title}`"
    :contain="contain"
    :max-height="maxHeight"
    :src="imageUrl"
    @error="imgError"
  />
</template>

<script>
export default {
  name: 'AssetImage',
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
    imageUrl: undefined
  }),
  created() {
    this.imageUrl = this.asset.imageUrl || require('@/assets/img-not-found.png')
  },
  methods: {
    imgError() {
      this.imageUrl = require('@/assets/img-not-found.png')
    }
  }
}
</script>
