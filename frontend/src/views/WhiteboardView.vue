<template>
  <div class="whiteboard-view">
    <WhiteboardCanvas />
  </div>
</template>

<script>
import WhiteboardCanvas from '../components/WhiteboardCanvas.vue'

export default {
  name: 'WhiteboardView',
  components: {
    WhiteboardCanvas,
  },
}
</script>

<style scoped>
.whiteboard-view {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: white;
}
</style>
