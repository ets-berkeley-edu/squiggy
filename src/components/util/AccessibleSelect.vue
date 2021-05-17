<template>
  <v-select
    :id="`${idPrefix}-select`"
    v-model="modelProxy"
    :clearable="!unclearable"
    :dense="dense"
    :disabled="disabled"
    :eager="true"
    :items="items"
    :item-text="itemText"
    :item-value="itemValue"
    :label="label"
    outlined
    @click:clear="onClear"
    @keydown.enter="onEnter"
  >
    <template #item="{item}">
      <span :id="`${idPrefix}-option-${item[itemValue]}`">{{ item[itemText] }}</span>
    </template>
    <template #selection="{item}">
      <div :id="`${idPrefix}-option-selected`">{{ item[itemText] }}</div>
    </template>
  </v-select>
</template>

<script>
export default {
  name: 'AccessibleSelect',
  props: {
    dense: {
      required: false,
      type: Boolean
    },
    disabled: {
      required: false,
      type: Boolean
    },
    idPrefix: {
      required: true,
      type: String
    },
    items: {
      required: true,
      type: Array
    },
    itemText: {
      default: 'text',
      required: false,
      type: String
    },
    itemValue: {
      default: 'value',
      required: false,
      type: String
    },
    label: {
      default: undefined,
      required: false,
      type: String
    },
    unclearable: {
      required: false,
      type: Boolean
    },
    value: {
      default: undefined,
      required: false,
      type: [Number, Object, String]
    }
  },
  data: () => ({
    model: undefined
  }),
  computed: {
    modelProxy: {
      get() {
        return this.model
      },
      set(value) {
        this.model = value
        this.$emit('input', this.model)
        if (this.model) {
          const item = this.$_.find(this.items, [this.itemValue, this.model])
          const name = this.$_.get(item, this.itemText) || this.model
          this.$announcer.polite(`${name} selected`)
        } else {
          this.$announcer.polite(`No ${this.label} selected`)
          this.$putFocusNextTick(`${this.idPrefix}-select`)
        }
      }
    }
  },
  created() {
    this.model = this.value
  },
  methods: {
    onEnter() {
      this.$announcer.polite('Menu is open.')
    },
    onClear() {
      this.$announcer.polite(`${this.label} cleared`)
    }
  }
}
</script>
