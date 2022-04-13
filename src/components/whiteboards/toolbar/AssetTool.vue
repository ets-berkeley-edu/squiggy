<template>
  <v-menu
    v-model="menu"
    close-on-content-click
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-add-asset"
        :color="menu ? 'primary' : 'white'"
        dense
        :disabled="disableAll"
        height="48px"
        rounded
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon :color="menu ? 'white' : 'grey'" icon="circle-plus" size="2x" />
        <span class="pl-2">Asset</span>
      </v-btn>
    </template>
    <v-card>
      <v-list>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <AddExistingAssets :watch-dialog="watchChildDialog" />
          </v-list-item-action>
        </v-list-item>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <UploadNewAsset :watch-dialog="watchChildDialog" />
          </v-list-item-action>
        </v-list-item>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <AddLinkAsset :watch-dialog="watchChildDialog" />
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
  data: () => ({
    menu: false,
    toggle: false
  }),
  methods: {
    watchChildDialog(isOpen) {
      if (isOpen) {
        // If secondary dialog is opening then close this menu.
        this.menu = false
      }
    }
  }
}
</script>
