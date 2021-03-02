<template>
  <div class="text-center">
    <h1>Squiggy says HELLO</h1>
    <div class="d-flex flex-column justify-space-between align-center">
      <v-slider
        v-model="width"
        class="align-self-stretch"
        min="200"
        max="500"
        step="1"
      ></v-slider>
      <v-img
        :aspect-ratio="16/9"
        :width="width"
        src="@/assets/hello.jpg"
      ></v-img>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Squiggy',
  data: () => ({
    width: 300,
  }),
  created() {
    this.$ready()
  }
}
</script>
