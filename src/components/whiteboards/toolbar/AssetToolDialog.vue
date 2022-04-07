<template>
  <div>
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      offset-y
      top
    >
      <template #activator="{on, attrs}">
        <v-btn
          id="toolbar-add-asset"
          :disabled="disableAll"
          icon
          v-bind="attrs"
          v-on="on"
        >
          <font-awesome-icon icon="circle-plus" />
          <span class="pl-2">Asset</span>
        </v-btn>
      </template>
      <v-card>
        <v-card-text>
          <h2 id="modal-header" class="sr-only">Choose the type of asset you want to upload</h2>
          <v-btn
            id="toolbar-add-existing-assets"
            @click="openAddExisting"
            @keypress.enter="openAddExisting"
          >
            <font-awesome-icon icon="bars" />
            <span class="pl-2">Use existing</span>
          </v-btn>

          <UploadNewAsset />
          <AddLinkAsset />
        </v-card-text>
      </v-card>
    </v-menu>
    <AddExistingAssets
      :after-save="afterAddExistingAssets"
      :on-cancel="onCancelAddExisting"
      :open="isOpenAddExisting"
    />
  </div>
</template>

<script>
import AddExistingAssets from '@/components/whiteboards/toolbar/AddExistingAssets'
import AddLinkAsset from '@/components/whiteboards/toolbar/AddLinkAsset'
import Whiteboarding from '@/mixins/Whiteboarding'
import UploadNewAsset from '@/components/whiteboards/toolbar/UploadNewAsset'

export default {
  name: 'AssetToolDialog',
  mixins: [Whiteboarding],
  components: {AddExistingAssets, AddLinkAsset, UploadNewAsset},
  data: () => ({
    isOpenAddExisting: false,
    menu: false
  }),
  methods: {
    afterAddExistingAssets() {
      this.menu = false
      this.isOpenAddExisting = false
    },
    onCancelAddExisting() {
      this.isOpenAddExisting = false
      this.menu = true
      this.$announcer.polite('Canceled.')
    },
    openAddExisting() {
      this.menu = false
      this.isOpenAddExisting = true
      this.$announcer.polite('Open Add Existing Assets menu.')
    }
  }
}
</script>
