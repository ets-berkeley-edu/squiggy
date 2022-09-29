<template>
  <div>
    <router-link v-slot="{navigate}" :to="linkBack()" custom>
      <v-btn
        id="asset-library-btn"
        class="bg-transparent pl-0"
        :disabled="disabled"
        elevation="0"
        @click="navigate"
        @keypress.enter="navigate"
      >
        <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
        Back to {{ previousTool === 'impactStudio' ? 'Impact Studio' : 'Asset Library' }}
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
  data: () => ({
    previousTool: null
  }),
  methods: {
    linkBack() {
      if (this.previousTool === 'impactStudio') {
        return '/impact_studio'
      } else {
        return this.anchor ? `/assets?anchor=${this.anchor}` : '/assets'
      }
    }
  },
  created() {
    this.previousTool = this.$_.get(this.$route.query, 'from') || 'assetLibrary'
  }
}
</script>
