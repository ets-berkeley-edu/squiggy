<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <AddExistingAssets
        :after-save="afterAddExistingAssets"
        :on-cancel="onCancelAddExisting"
        :open="isOpenAddExisting"
      />
      <v-btn
        id="toolbar-add-asset"
        :disabled="disableAll"
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon icon="circle-plus" size="2x" />
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
        <v-btn
          id="toolbar-upload-new-asset"
          @click="openAddExisting"
          @keypress.enter="uploadFiles"
        >
          <!-- Use uploadFiles() function imported from old SuiteC -->
          <font-awesome-icon icon="laptop" />
          <span class="pl-2">Upload New</span>
        </v-btn>
        <v-btn
          id="toolbar-upload-new-asset"
          @click="openAddExisting"
          @keypress.enter="openAddExisting"
        >
          <font-awesome-icon icon="chain" />
          <span class="pl-2">Add Link</span>
        </v-btn>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import AddExistingAssets from '@/components/whiteboards/toolbar/AddExistingAssets'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'AssetToolDialog',
  mixins: [Whiteboarding],
  components: {AddExistingAssets},
  data: () => ({
    menu: false,
    isOpenAddExisting: false
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
