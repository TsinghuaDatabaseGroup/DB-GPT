<template>
  <div class="group_node">
    <div class="group_node_header" :style="itemData.userData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.9);': 'background-color: #3C3A3A;'">
      {{itemData.userData.title}}
    </div>
    <div class="group_content">
      <div v-for="(item, index) in expertData" :style="item.isRuning ? '' : 'opacity: 0.5'" :key="index"
           class="group_content_item">

        <template v-if="item.isRuning">
          <el-popover
              placement="top-start"
              title=""
              trigger="click"
             >
            <OneChat style="width: 360px; height: 400px; border-radius: 8px; overflow: hidden; z-index: 9999999999" :messages="item.messages"
                     :sender="item.title"></OneChat>
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

import OneChat from "@/chat/OneChat";

export default {
  name: "agent_group_node",
  components: {
    OneChat
  },
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
      defaultExpertData: [
        {
          title: 'CpuExpert',
          subTitle: 'CpuExpert',
          avatar: 'cpu_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'MemoryExpert',
          subTitle: 'MemoryExpert',
          avatar: 'mem_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'IoExpert',
          subTitle: 'IoExpert',
          avatar: 'io_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'IndexExpert',
          subTitle: 'IndexExpert',
          avatar: 'index_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'ConfigExpert',
          subTitle: 'ConfigurationExpert',
          avatar: 'configuration_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'QueryExpert',
          subTitle: 'QueryExpert',
          avatar: 'query_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'WorkloadExpert',
          subTitle: 'WorkloadExpert',
          avatar: 'workload_robot.webp',
          isRuning: false,
          role: ''
        },
        {
          title: 'WriteExpert',
          subTitle: 'WriteExpert',
          avatar: 'mem_robot.webp',
          isRuning: false,
          role: ''
        },
      ],
      expertData: []
    }
  },
  watch: {
    itemData: {
      handler(newVal, oldVal) {
        this.expertData = JSON.parse(JSON.stringify(this.defaultExpertData));
        if(newVal.userData.expertData) {
          // 将expertData中的name和role提取出来，如果expertData中的name和expertData中的subTitle相同，则将role赋值给expertData中的role，且将isRuning设置为true, 否则设置为false
          this.expertData.forEach((item) => {
            newVal.userData.expertData.forEach((expertItem) => {
              if(item.subTitle === expertItem.name) {
                item.isRuning = true;
                item.messages = expertItem.messages;
              }
            })
          })
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

.el-popover {
  background: transparent!important;
  padding: 0!important;
  border: none!important;
}

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
