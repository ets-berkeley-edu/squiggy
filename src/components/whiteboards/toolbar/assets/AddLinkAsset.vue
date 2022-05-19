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
            <v-col class="pb-2">
              <h2 id="modal-header">Add a Link</h2>
              <div class="pt-2 subtitle-1">
                A new asset will be created and then added to this whiteboard.
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-col class="pt-5" cols="2">
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
                :error="$_.trim(asset.url) ? !isValidURL(asset.url) : false"
                hide-details
                maxlength="2048"
                outlined
                required
                :rules="urlRules"
                @blur="ensureUrlPrefix"
                @keydown.enter="onClickSave"
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
                  <span v-if="title.length">({{ 255 - asset.title.length }} remaining)</span>
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
                <div class="caption">Add context to your link with plain text or #keywords.</div>
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
            <v-col cols="2"></v-col>
            <v-col cols="10">
              <v-checkbox
                :id="`asset-visible-checkbox`"
                v-model="asset.visible"
                hide-details
              >
                <template #label>
                  Also add this link to Asset Library
                </template>
              </v-checkbox>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="d-flex justify-end pt-5">
              <div class="pr-1">
                <v-btn
                  id="save-btn"
                  color="primary"
                  :disabled="disableSave"
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
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import {createLinkAsset} from '@/api/assets'

export default {
  name: 'AddLinkAsset',
  mixins: [Utils, Whiteboarding],
  components: {AccessibleSelect},
  data: () => ({
    asset: {
      categoryId: undefined,
      description: undefined,
      title: '',
      url: '',
      visible: false
    },
    dialog: false,
    isSaving: false,
    title: 'Add Link Asset'
  }),
  computed: {
    disableSave() {
      return this.isSaving || !this.$_.trim(this.asset.title) || !this.isValidURL(this.asset.url)
    }
  },
  methods: {
    ensureUrlPrefix() {
      if (this.asset.url && this.asset.url.indexOf('://') === -1) {
        this.asset.url = `http://${this.asset.url}`
      }
    },
    onClickCancel() {
      this.dialog = false
      this.$announcer.polite('Canceled')
    },
    onClickSave() {
      if (!this.disableSave) {
        this.$announcer.polite('Creating asset...')
        this.isSaving = true
        this.ensureUrlPrefix()
        createLinkAsset(
          this.asset.categoryId,
          this.asset.description,
          this.asset.title,
          this.asset.url,
          this.asset.visible
        ).then(asset => {
          this.addAsset(asset).then(() => {
            this.$announcer.polite('Link asset created.')
            this.asset = {
              categoryId: undefined,
              description: undefined,
              title: '',
              url: undefined
            }
            this.dialog = false
            this.isSaving = false
          })
        })
      }
    },
  }
}
</script>
