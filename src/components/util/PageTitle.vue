<template>
  <h1>
    <span
      id="page-title"
      :class="{'text-h4': text.length > 40, cssClass: true}"
      tabindex="0"
    >
      {{ text }}
    </span>
  </h1>
</template>

<script>
export default {
  name: 'PageTitle',
  props: {
    cssClass: {
      default: '',
      required: false,
      type: String
    },
    text: {
      required: true,
      type: String
    }
  }
}
</script>
