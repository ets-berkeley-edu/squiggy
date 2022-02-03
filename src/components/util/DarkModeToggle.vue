<template>
  <v-btn id="toggle-dark-mode-btn" icon @click="$vuetify.theme.dark = !$vuetify.theme.dark">
    <span class="sr-only">Turn dark mode {{ $vuetify.theme.dark ? 'off' : 'on' }}.</span>
    <font-awesome-icon :class="{'yellow--text': $vuetify.theme.dark}" :icon="$vuetify.theme.dark ? 'sun' : 'moon'" />
  </v-btn>
</template>

<script>
export default {
  name: 'DarkModeToggle'
}
</script>
