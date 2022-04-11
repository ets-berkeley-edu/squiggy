<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-add-asset"
        color="white"
        dense
        :disabled="disableAll"
        height="48px"
        rounded
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon :color="menu ? 'black' : 'grey'" icon="circle-plus" size="2x" />
        <span class="pl-2">Asset</span>
      </v-btn>
    </template>
    <v-card>
      <v-card-text>
        <h2 class="sr-only">Choose asset(s) to upload</h2>
        <AddExistingAssets />
        <UploadNewAsset />
        <AddLinkAsset />
      </v-card-text>
    </v-card>
  </v-menu>
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
    menu: false
  })
}
</script>
