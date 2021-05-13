<template>
  <div>
    <router-link v-slot="{navigate}" :to="linkBack()" custom>
      <v-btn
        id="asset-library-btn"
        class="bg-transparent"
        :disabled="disabled"
        elevation="0"
        @click="navigate"
        @keypress.enter="navigate"
      >
        <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
        Back to Asset Library
      </v-btn>
    </router-link>
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
    linkBack() {
      return this.anchor ? `/assets?anchor=${this.anchor}` : '/assets'
    }
  }
}
</script>
