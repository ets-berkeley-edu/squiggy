<template>
  <v-dialog
    v-model="dialog"
    scrollable
    transition="dialog-bottom-transition"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-text"
        :disabled="disableAll"
        v-bind="attrs"
        value="text"
        v-on="on"
      >
        <span class="sr-only">Text</span>
        <font-awesome-icon icon="font" />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2>Add asset(s)</h2>
      </v-card-title>
      <v-card-text v-if="isReady">
        <div id="dialog-header" class="sr-only">Select Text Size and Color</div>
        <v-container>
          <v-row>
            <v-col cols="3">Size</v-col>
            <v-col cols="9">
              <AccessibleSelect
                :dense="true"
                :hide-details="true"
                id-prefix="tool-select-text-size"
                :items="[
                  {text: 'Normal', value: 14},
                  {text: 'Title', value: 36}
                ]"
                :unclearable="true"
                :value="fontSize"
                @input="v => (fontSize = v)"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col class="float-right" cols="3">Color</v-col>
            <v-col cols="9">
              <v-color-picker
                v-model="fill"
                class="ma-2"
                hide-canvas
                hide-inputs
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <div class="pb-3 pr-2">
          <v-btn
            id="add-text-btn"
            color="primary"
            :disabled="!isReady"
            @click="$_.noop"
          >
            Save<span class="sr-only"> text to whiteboard</span>
          </v-btn>
          <v-btn
            id="cancel-btn"
            :disabled="!isReady"
            text
            @click="cancel"
          >
            Cancel
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Context from '@/mixins/Context'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'TextToolDialog',
  components: {AccessibleSelect},
  mixins: [Context, Whiteboarding],
  data: () => ({
    element: undefined,
    dialog: false,
    isReady: false
  }),
  computed: {
    fill: {
      get() {
        return this.element.fill
      },
      set(value) {
        this.element.fill = value
        this.setObjectAttribute({attribute: 'fill', uid: this.uid, value: value})
      }
    },
    fontSize: {
      get() {
        return this.element.fontSize
      },
      set(value) {
        this.element.fontSize = value
        this.setObjectAttribute({attribute: 'fontSize', uid: this.uid, value: value})
      }
    }
  },
  watch: {
    dialog(isOpen) {
      if (isOpen) {
        this.add('text').then(element => {
          this.element = element
          this.$putFocusNextTick('dialog-header')
          this.isReady = true
        })
      } else {
        this.isReady = false
      }
      this.setDisableAll(isOpen)
    }
  },
  methods: {
    cancel() {
      this.delete(this.object).then(() => {
        this.dialog = undefined
      })
    }
  }
}
</script>
