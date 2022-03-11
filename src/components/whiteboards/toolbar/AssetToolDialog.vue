<template>
  <v-dialog v-model="dialog" attach="#toolbar">
    <template #activator="{on, attrs}">
      <AddExistingAssets
        :after-save="afterAddExistingAssets"
        :on-cancel="onCancelAddExisting"
        :open="isOpenAddExisting"
      />
      <v-btn
        id="toolbar-add-asset"
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
          @keypress.enter="openAddExisting"
        >
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
  </v-dialog>
</template>

<script>
import AddExistingAssets from '@/components/whiteboards/toolbar/AddExistingAssets'
import Context from '@/mixins/Context'

export default {
  name: 'AssetToolDialog',
  mixins: [Context],
  components: {AddExistingAssets},
  data: () => ({
    dialog: false,
    isOpenAddExisting: false
  }),
  methods: {
    afterAddExistingAssets() {
      this.dialog = false
      this.isOpenAddExisting = false
    },
    onCancelAddExisting() {
      this.isOpenAddExisting = false
      this.dialog = true
      this.$announcer.polite('Canceled dialog to Add Existing Assets.')
    },
    openAddExisting() {
      this.dialog = false
      this.isOpenAddExisting = true
      this.$announcer.polite('Open dialog to Add Existing Assets.')
    }
  }
}
</script>
