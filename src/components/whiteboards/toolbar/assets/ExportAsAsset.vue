<template>
  <v-dialog
    v-model="dialog"
    :close-on-content-click="false"
    width="500"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-export-to-asset-library-btn"
        class="justify-start w-100"
        color="white"
        elevation="0"
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon icon="images" size="lg" />
        <span class="pl-3">Export to Asset Library</span>
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pl-8 pt-8">
        <v-container v-if="!asset.id" fluid>
          <v-row>
            <v-col class="py-2" cols="12">
              <div class="align-center d-flex" :class="{'flex-column': whiteboard.thumbnailUrl}">
                <img v-if="whiteboard.thumbnailUrl" alt="Whiteboard thumbnail image" :src="whiteboard.thumbnailUrl" />
                <font-awesome-icon
                  v-if="!whiteboard.thumbnailUrl"
                  color="primary"
                  icon="images"
                  size="2x"
                />
                <h2 id="modal-header" class="pl-2">Export to Asset Library</h2>
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-col class="pt-5" cols="2">
              <label class="float-right" for="asset-title-input">
                Title
                <font-awesome-icon
                  aria-label="Icon indicates required field"
                  class="deep-orange--text icon-denotes-required"
                  icon="asterisk"
                  size="xs"
                />
              </label>
            </v-col>
            <v-col cols="10">
              <v-text-field
                id="asset-title-input"
                v-model="asset.title"
                hide-details
                maxlength="255"
                outlined
                required
              />
              <div class="pl-1">
                <span
                  :aria-live="asset.title.length === 255 ? 'assertive' : null"
                  class="font-size-12"
                  :class="asset.title.length === 255 ? 'red--text' : 'text--secondary'"
                  role="alert"
                >
                  255 character limit
                  <span v-if="asset.title.length">({{ 255 - asset.title.length }} remaining)</span>
                </span>
              </div>
            </v-col>
          </v-row>
          <v-row v-if="categories.length">
            <v-col class="pt-5" cols="2">
              <label class="float-right" for="asset-category-select">Category</label>
            </v-col>
            <v-col cols="10">
              <AccessibleSelect
                id-prefix="asset-category"
                hide-details
                :items="categories"
                item-text="title"
                item-value="id"
                label="Select..."
                :value="asset.categoryId"
                @input="c => (asset.categoryId = c)"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col class="pt-5" cols="2">
              <label class="float-right" for="asset-description-textarea">Description</label>
            </v-col>
            <v-col cols="10">
              <div class="d-flex flex-column flex-column-reverse">
                <div class="caption">Add some more context to your link. You can use plain text or #keywords</div>
                <div>
                  <v-textarea
                    id="asset-description-textarea"
                    v-model="asset.description"
                    hide-details
                    outlined
                  />
                </div>
              </div>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="d-flex justify-end pt-5">
              <div class="pr-1">
                <v-btn
                  id="save-btn"
                  color="primary"
                  :disabled="isExporting"
                  @click="onClickSave"
                  @keypress.enter="onClickSave"
                >
                  <span v-if="isExporting">
                    <font-awesome-icon class="mr-2" icon="spinner" spin />
                    Exporting...
                  </span>
                  <span v-if="!isExporting">
                    <font-awesome-icon class="mr-2" icon="check" />
                    Export
                  </span>
                </v-btn>
              </div>
              <div>
                <v-btn
                  id="cancel-btn"
                  :disabled="isExporting"
                  text
                  @click="onClickCancel"
                  @keypress.enter="onClickCancel"
                >
                  Cancel
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-container>
        <div v-if="asset.id">
          <ExportSummary :asset="asset" :on-click-close="onClickClose" />
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import ExportSummary from '@/components/whiteboards/ExportSummary'
import Whiteboarding from '@/mixins/Whiteboarding'
import {exportAsset} from '@/api/whiteboards'

export default {
  name: 'ExportAsAsset',
  mixins: [Whiteboarding],
  components: {AccessibleSelect, ExportSummary},
  data: () => ({
    asset: {
      categoryId: undefined,
      description: '',
      title: ''
    },
    isExporting: false,
    dialog: false
  }),
  created() {
    this.asset.title = this.whiteboard.title
  },
  methods: {
    onClickCancel() {
      this.dialog = false
      this.$announcer.polite('Canceled')
    },
    onClickClose() {
      this.dialog = false
      this.$announcer.polite('Closed')
    },
    onClickSave() {
      this.$announcer.polite('Exporting...')
      this.isExporting = true
      const categoryIds = this.asset.categoryId ? [this.asset.categoryId] : []
      exportAsset(
        categoryIds,
        this.asset.description,
        this.asset.title,
        this.whiteboard.id
      ).then(asset => {
        this.$announcer.polite('Asset created.')
        this.isExporting = false
        this.asset = asset
      })
    },
  }
}
</script>
