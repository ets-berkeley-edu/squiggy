<template>
  <div>
    <v-btn
      id="asset-library-btn"
      class="bg-transparent"
      :disabled="disabled"
      elevation="0"
      @click="goBack"
      @keypress.enter="goBack"
    >
      <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
      Back to Asset Library
    </v-btn>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'BackToAssetLibrary',
  mixins: [Utils],
  props: {
    anchor: {
      default: undefined,
      required: false,
      type: String
    },
    disabled: {
      required: false,
      type: Boolean
    }
  },
  methods: {
    goBack() {
      this.go( '/assets', this.anchor ? {'anchor': this.anchor} : {})
    }
  }
}
</script>
