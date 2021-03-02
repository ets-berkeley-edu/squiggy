<template>
  <h1>
    <span id="page-title" :class="{'text-h4': text.length > 40}" tabindex="0"> {{ text }}</span>
  </h1>
</template>

<script>
export default {
  name: 'PageTitle',
  props: {
    text: {
      required: true,
      type: String
    }
  }
}
</script>
