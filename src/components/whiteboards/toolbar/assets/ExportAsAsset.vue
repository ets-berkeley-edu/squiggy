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
        text
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon icon="images" size="2x" />
        <span class="pl-3">Export to Asset Library</span>
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pl-8 pt-8">
        <v-container fluid>
          <v-row>
            <v-col class="pt-5" cols="12">
              <img
                v-if="whiteboard.thumbnailUrl"
                :src="whiteboard.thumbnailUrl"
              />
              <div
                v-if="!whiteboard.thumbnailUrl"
                class="text-center col-list-item-thumbnail-default col-list-item-no-metadata"
              >
                <font-awesome-icon icon="calendar" size="2x" />
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
                maxlength="255"
                outlined
                required
              />
            </v-col>
          </v-row>
          <v-row v-if="categories.length">
            <v-col class="pt-5" cols="2">
              <label class="float-right" for="asset-category-select">Category</label>
            </v-col>
            <v-col cols="10">
              <AccessibleSelect
                id-prefix="asset-category"
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
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Whiteboarding from '@/mixins/Whiteboarding'
import {exportAsset} from '@/api/whiteboards'

export default {
  name: 'ExportAsAsset',
  mixins: [Whiteboarding],
  components: {AccessibleSelect},
  props: {
    watchDialog: {
      default: () => {},
      required: false,
      type: Function
    }
  },
  data: () => ({
    asset: {
      categoryId: undefined,
      description: undefined,
      title: undefined
    },
    isExporting: false,
    dialog: false
  }),
  watch: {
    dialog(value) {
      this.watchDialog(value)
    }
  },
  methods: {
    onClickCancel() {
      this.dialog = false
      this.$announcer.polite('Canceled')
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
      ).then(() => {
        this.$announcer.polite('Asset created.')
        this.dialog = false
        this.isExporting = false
      })
    },
  }
}
</script>
