<template>
  <v-dialog
    v-model="dialog"
    :close-on-content-click="false"
    width="500"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-asset-add-link"
        :color="mode === 'link' ? 'white' : 'primary'"
        icon
        :title="title"
        value="link"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">{{ title }}</span>
        <font-awesome-icon
          :color="{'white': mode === 'link'}"
          icon="chain"
          size="lg"
        />
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="pl-8 pt-8">
        <v-container fluid>
          <v-row>
            <v-col class="pt-5" cols="2">
              <h2 id="modal-header" class="sr-only">Choose the type of asset you want to upload</h2>
              <label class="float-right" for="asset-url-input">
                URL
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
                id="asset-url-input"
                v-model="asset.url"
                maxlength="255"
                outlined
                required
              />
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
                  :disabled="isSaving"
                  @click="onClickSave"
                  @keypress.enter="onClickSave"
                >
                  <font-awesome-icon class="mr-2" icon="check" />
                  Save<span class="sr-only"> asset to whiteboard</span>
                </v-btn>
              </div>
              <div>
                <v-btn
                  id="cancel-btn"
                  :disabled="isSaving"
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
import {createLinkAsset} from '@/api/assets'

export default {
  name: 'AddLinkAsset',
  mixins: [Whiteboarding],
  components: {AccessibleSelect},
  data: () => ({
    asset: {
      categoryId: undefined,
      description: undefined,
      title: undefined,
      url: undefined
    },
    dialog: false,
    isSaving: false,
    title: 'Add Link Asset'
  }),
  methods: {
    onClickCancel() {
      this.dialog = false
      this.$announcer.polite('Canceled')
    },
    onClickSave() {
      this.$announcer.polite('Creating asset...')
      this.isSaving = true
      createLinkAsset(
        this.asset.categoryId,
        this.asset.description,
        this.asset.title,
        this.asset.url
      ).then(asset => {
        this.addAsset(asset).then(() => {
          this.$announcer.polite('Link asset created.')
          this.asset = {
            categoryId: undefined,
            description: undefined,
            title: undefined,
            url: undefined
          }
          this.isSaving = false
        })
      })
    },
  }
}
</script>
