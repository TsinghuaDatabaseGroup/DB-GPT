<template>
  <div class="node">
    <div class="header" :style="itemData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.8);': 'background-color: #3C3A3A;'">
      {{itemData.title}}
    </div>
    <div class="content">
      {{itemData.content}}
    </div>
    <div v-if="itemData.isRuning" class="blinking-dot"></div>
  </div>
</template>

<script>

export default {
  name: "title-content-node",
  props: {
    itemData: {
      type: Object,
    },
    canvasNode: {
      type: Object
    }
  },
  components: {
  },
  methods: {}
};
</script>

<style>

.blinking-dot {
  width: 12px;
  height: 12px;
  background-color: #67C23A;
  border-radius: 50%;
  position: absolute;
  top: 8px;
  right:8px;
  animation: breathe 1.5s infinite;
}

@keyframes breathe {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.2;
  }
}

.butterflie-circle-endpoint {
  background: #67C23A !important;
  border: 1px solid #67C23A !important;
}

.node {
  width: 240px;
  box-shadow: 0 2px 3px 0 rgba(0,112,204,0.06);;
  border-radius:8px;
  overflow: hidden;
  position: relative;
}

.header {
  position: relative;
  padding: 5px 20px;
  border-radius: 5px 5px 0 0;
  color: #FFF;
  border: none;
  min-height: 10px;
  background-color: #3C3A3A;
  text-align: center;
  font-size: 12px;
}

.content {
  position: relative;
  color: #ffffff;
  padding: 10px;
  border-top: 2px solid #000000;
  border-radius: 0 0 5px 5px;
  min-height: 60px;
  font-size: 12px;
  background-color: #3C3A3A;
}

</style>
