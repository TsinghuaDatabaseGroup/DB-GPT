<template>
  <div class="node">
    <div class="header" :style="itemData.userData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.9);': 'background-color: #3C3A3A;'">
      {{itemData.userData.title}}
    </div>
    <div class="content">
      {{itemData.userData.content}}
    </div>
    <div v-if="itemData.userData.isRuning" class="blinking-dot"></div>
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
  font-size: 14px;
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
  word-break: break-all;
  height: 60px;
  text-overflow: ellipsis;
  overflow: hidden;
}

</style>
