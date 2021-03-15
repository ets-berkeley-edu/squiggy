<template>
  <v-data-table
    :headers="[{value: 'key'}, {value: 'value'}]"
    :hide-default-footer="true"
    :hide-default-header="true"
    :items="configs"
    :items-per-page="50"
  />
</template>

<script>
export default {
  name: 'Configs',
  data: () => ({
    configs: []
  }),
  created() {
    this.$_.each(this.$config, (value, key) => {
      this.configs.push({key, value: this.stringify(value)})
    })
  },
  methods: {
    stringify(v) {
      if (Array.isArray(v)) {
        return this.$_.join(v, ',')
      } else if (v && typeof v === 'object') {
        return JSON.stringify(v)
      }
      return v
    }
  }
}
</script>
