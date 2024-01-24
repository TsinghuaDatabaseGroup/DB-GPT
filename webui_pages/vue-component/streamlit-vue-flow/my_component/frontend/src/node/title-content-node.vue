<template>
  <div class="node">
    <div class="header">
      {{itemData.title || '标题'}}
    </div>
    <div class="content">
      {{itemData.content || '内容内容内容内容内容内容内容内容内容内容内容'}}
    </div>
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

.butterflie-circle-endpoint {
  background: #67C23A !important;
  border: 1px solid #67C23A !important;
}

.node {
  max-width: 200px;
  min-width: 60px;
  box-shadow: 0 2px 3px 0 rgba(0,112,204,0.06);;
  background-color: #fff;
  border-radius:8px;
  overflow: hidden;
  border: 1px solid #aaa;
}

.header {
  padding: 5px;
  border-radius: 5px 5px 0 0;
  color: #FFF;
  min-height: 10px;
  background-color: #F66902;
  text-align: center;
  font-size: 12px;
}

.content {
  color: #222;
  padding: 10px;
  border: 1px solid #D9D9D9;
  border-top: none;
  border-radius: 0 0 5px 5px;
  min-height: 60px;
  font-size: 12px;
}

</style>
