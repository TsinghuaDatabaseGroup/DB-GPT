<template>
  <div class="c-flex-column c-align-items-center" style="padding: 20px;">
    <div>
      <img src="@/assets/dba_robot.webp">
    </div>

    <div class="c-flex-row c-justify-content-between" style="width: 100%; margin-top: 10px">
      <img src="@/assets/cpu_robot.webp">
      <img src="@/assets/mem_robot.webp">
      <img src="@/assets/io_robot.webp">
    </div>
    <div
      class="c-flex-column"
      style="width: 100%; margin-top: 10px; border-radius: 8px; border: 2px solid lightcoral;
          height: calc(100% - 220px);"
    >
      <span style="width: 100%; text-align: center; margin-top: 5px">圆桌讨论区</span>
      <Chat :messages="messages" />
    </div>

    <div class="c-flex-row c-justify-content-left" style="width: 100%; margin-top: 10px">
      <img src="@/assets/dba_robot.webp" style="width: 30px; height: 30px;">
      <span style="color: #333333; margin-left: 5px; line-height: 20px">我们团队已经生成该异常的详细报告，可点击<span style="color: #007AFF">下载</span>进行查看</span>
    </div>

  </div>
</template>

<script>

import Chat from '@/components/Chat'
export default {
  name: 'RoundTable',
  components: { Chat },
  data() {
    return {
      messages: [
        { sender: 'Chief DBA', content: { diagnose: '大家都思考完了，开始你们的讨论吧！' }, type: 'message', time: '2023-09-10 21:44:23' },
        { sender: 'CPU Agent', content: { diagnose: '从CPU的角度上分析，我发现XXX指标有问题' }, type: 'message', time: '2023-09-10 21:44:23' }]
    }
  }
}
</script>

<style scoped>

</style>
