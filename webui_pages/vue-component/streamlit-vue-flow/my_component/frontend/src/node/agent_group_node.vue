<template>
  <div class="group_node">
    <div class="group_node_header" :style="itemData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.8);': 'background-color: #3C3A3A;'">
      {{itemData.title}}
    </div>
    <div class="group_content">
      <div v-for="(item, index) in agentData" :style="'opacity: ' + item.opacity" :key="index" class="group_content_item">
        <img class="group_content_item_avatar" :src="require(`@/assets/${item.avatar}`)">
        <div class="group_content_item_text">{{item.title}}</div>
      </div>
    </div>
    <div v-if="itemData.isRuning" class="blinking-dot"></div>
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
      agentData: [
        {
          title: 'Cpu Expert',
          avatar: 'cpu_robot.webp',
          opacity: 1
        },
        {
          title: 'Mex Expert',
          avatar: 'mem_robot.webp',
          opacity: 1
        },
        {
          title: 'Index Expert',
          avatar: 'index_robot.webp',
          opacity: 1
        },
        {
          title: 'IO Expert',
          avatar: 'io_robot.webp',
          opacity: 0.5
        },
        {
          title: 'Net Expert',
          avatar: 'net_robot.webp',
          opacity: 0.5
        },
        {
          title: 'Query Expert',
          avatar: 'query_robot.webp',
          opacity: 1
        },
        {
          title: 'Workload Expert',
          avatar: 'workload_robot.webp',
          opacity: 0.5
        },
        {
          title: 'DBA Expert',
          avatar: 'dba_robot.webp',
          opacity: 0.5
        }
      ]
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

.group_node {
  width: 380px;
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
  font-size: 12px;
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
