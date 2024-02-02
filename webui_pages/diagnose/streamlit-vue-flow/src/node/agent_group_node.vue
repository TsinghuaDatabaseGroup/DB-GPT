<template>
  <div class="group_node">
    <div class="group_node_header" :style="itemData.userData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.9);': 'background-color: #3C3A3A;'">
      {{itemData.userData.title}}
    </div>
    <div class="group_content">
      <div v-for="(item, index) in expertData" :style="expertUsedDataTitle.indexOf(item.subTitle) >= 0 ? '' : 'opacity: 0.5'" :key="index"
           class="group_content_item">

        <template v-if="expertUsedDataTitle.indexOf(item.subTitle) >= 0">
          <el-popover
              placement="top-start"
              title=""
              width="200"
              trigger="hover"
             >
            <div style="font-size: 12px; color: #666666; white-space: pre-wrap; word-break: break-all"></div>
            <div slot="reference" :class="itemData.isDiagnosing ? 'blinking-avatar-dot' : 'avatar-dot' ">
              <img class="group_content_item_avatar" :src="require(`@/assets/${item.avatar}`)">
            </div>
          </el-popover>
        </template>
        <template v-else>
          <div>
            <img class="group_content_item_avatar" :src="require(`@/assets/${item.avatar}`)">
          </div>
        </template>
        <div class="group_content_item_text">{{item.title}}</div>
      </div>
    </div>
    <div v-if="itemData.userData.isRuning && itemData.isDiagnosing" class="blinking-dot"></div>
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
          subTitle: 'CpuExpert',
          avatar: 'cpu_robot.webp',
        },
        {
          title: 'MemoryExpert',
          subTitle: 'MemoryExpert',
          avatar: 'mem_robot.webp',
        },
        {
          title: 'IoExpert',
          subTitle: 'IoExpert',
          avatar: 'io_robot.webp',
        },
        {
          title: 'IndexExpert',
          subTitle: 'IndexExpert',
          avatar: 'index_robot.webp',
        },
        {
          title: 'ConfigExpert',
          subTitle: 'ConfigurationExpert',
          avatar: 'configuration_robot.webp',
        },
        {
          title: 'QueryExpert',
          subTitle: 'QueryExpert',
          avatar: 'query_robot.webp',
        },
        {
          title: 'WorkloadExpert',
          subTitle: 'WorkloadExpert',
          avatar: 'workload_robot.webp',
        },
        {
          title: 'WriteExpert',
          subTitle: 'WriteExpert',
          avatar: 'mem_robot.webp',
        },
      ],
      expertUsedDataTitle: []
    }
  },
  watch: {
    itemData: {
      handler(newVal, oldVal) {
        if(newVal.userData.expertData) {
          this.expertUsedDataTitle = newVal.userData.expertData.map(item => item.name.lowerCase());
        }
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

.avatar-dot {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border: 3px solid #67C23A;
}

.blinking-avatar-dot {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}

.blinking-avatar-dot::after {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  width: 100%;
  height: 100%;
  border: 3px solid #67C23A;
  opacity: 0;
  border-radius: 50%;
  animation: breathing 1.5s infinite;
}

@keyframes breathing {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.2;
  }
}

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
  margin-top: 2px;
}

</style>
