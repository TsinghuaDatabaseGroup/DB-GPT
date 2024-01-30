<template>
  <div class="group_node">
    <div class="group_node_header" :style="itemData.userData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.9);': 'background-color: #3C3A3A;'">
      {{itemData.userData.title}}
    </div>
    <div class="group_content">
      <div v-for="(item, index) in expertData" :style="expertUsedData.indexOf(item.subTitle) >= 0 ? '' : 'opacity: 0.5'" :key="index"
           class="group_content_item">
        <img class="group_content_item_avatar" :src="require(`@/assets/${item.avatar}`)">
        <div class="group_content_item_text">{{item.title}}</div>
      </div>
    </div>
    <div v-if="itemData.userData.isRuning" class="blinking-dot"></div>
  </div>
</template>

<script>

export default {
  name: "agent_group_node",
  props: {
    itemData: {
      type: Object,
    },
    canvasNode: {
      type: Object
    }
  },
  data() {
    return {
      expertData: [
        {
          title: 'CpuExpert',
          subTitle: 'cpu expert',
          avatar: 'cpu_robot.webp',
        },
        {
          title: 'MemoryExpert',
          subTitle: 'memory expert',
          avatar: 'mem_robot.webp',
        },
        {
          title: 'IoExpert',
          subTitle: 'io expert',
          avatar: 'io_robot.webp',
        },
        {
          title: 'IndexExpert',
          subTitle: 'index expert',
          avatar: 'index_robot.webp',
        },
        {
          title: 'ConfigExpert',
          subTitle: 'configuration expert',
          avatar: 'configuration_robot.webp',
        },
        {
          title: 'QueryExpert',
          subTitle: 'query expert',
          avatar: 'query_robot.webp',
        },
        {
          title: 'WorkloadExpert',
          subTitle: 'workload expert',
          avatar: 'workload_robot.webp',
        },
        {
          title: 'WriteExpert',
          subTitle: 'write expert',
          avatar: 'mem_robot.webp',
        },
      ],
      expertUsedData: []
    }
  },
  watch: {
    itemData: {
      handler(newVal, oldVal) {
        this.expertUsedData = newVal.userData.expertData || []
        console.log('Args changed from', oldVal, 'to', newVal);
      },
      deep: true,
      immediate: true
    },
  },
  methods: {}
};
</script>

<style>



.group_node {
  width: 400px;
  border-radius:8px;
  overflow: hidden;
  position: relative;
}

.group_node_header {
  position: relative;
  padding: 5px 20px;
  border-radius: 5px 5px 0 0;
  border: none;
  min-height: 10px;
  color: #ffffff;
  background-color: #3C3A3A;
  text-align: center;
  font-size: 12px;
}

.group_content {
  position: relative;
  color: #ffffff;
  padding: 10px;
  border-top: 2px solid #000000;
  border-radius: 0 0 5px 5px;
  min-height: 60px;
  text-align: center;
  background-color: #3C3A3A;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  flex-wrap: wrap;
}

.group_content_item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 10px;
  margin-bottom: 10px;
}

.group_content_item_avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%
}
.group_content_item_text {
  color: #ffffff;
  font-size: 12px;
  text-align: center;
}

</style>
