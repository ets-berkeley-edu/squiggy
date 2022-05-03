<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-add-asset"
        :color="mode === 'assets' ? 'white' : 'primary'"
        icon
        :title="title"
        value="assets"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">{{ title }}</span>
        <font-awesome-icon
          :color="{'white': mode === 'assets'}"
          icon="images"
          size="lg"
        />
      </v-btn>
    </template>
    <v-card>
      <v-list>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <AddExistingAssets />
          </v-list-item-action>
        </v-list-item>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <UploadNewAsset />
          </v-list-item-action>
        </v-list-item>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <AddLinkAsset />
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import AddExistingAssets from '@/components/whiteboards/toolbar/assets/AddExistingAssets'
import AddLinkAsset from '@/components/whiteboards/toolbar/assets/AddLinkAsset'
import Whiteboarding from '@/mixins/Whiteboarding'
import UploadNewAsset from '@/components/whiteboards/toolbar/assets/UploadNewAsset'

export default {
  name: 'AssetTool',
  mixins: [Whiteboarding],
  components: {AddExistingAssets, AddLinkAsset, UploadNewAsset},
  props: {
    hidden: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    title: 'Add or create assets for your whiteboard',
    toggle: false
  }),
  computed: {
    menu: {
      get() {
        return this.mode === 'assets'
      },
      set(value) {
        if (value) {
          this.setMode('assets')
          this.$putFocusNextTick('menu-header')
        } else {
          this.resetSelected()
          this.setMode('move')
        }
        this.setDisableAll(value)
      }
    }
  },
  beforeDestroy() {
    this.resetSelected()
    this.setDisableAll(false)
  }
}
</script>
