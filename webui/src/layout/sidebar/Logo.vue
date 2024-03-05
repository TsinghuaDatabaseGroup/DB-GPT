<template>
  <div class="sidebar-logo-container">
    <transition name="sidebar-logo-fade">
      <el-image src="https://pica.zhimg.com/v2-e626e7f7870f19081ed4fc43bfb9c642_r.jpg?source=2c26e567" />
    </transition>
  </div>
</template>

<script setup lang="ts">
import { reactive, toRefs } from 'vue'
import { useBasicStore } from '@/store/basic'
import SvgIcon from '@/icons/SvgIcon.vue'
const { settings } = useBasicStore()
defineProps({
  //是否折叠
  collapse: {
    type: Boolean,
    required: true
  }
})
const state = reactive({
  title: settings.title,
  //src/icons/common/sidebar-logo.svg
  logo: 'sidebar-logo'
})
//export to page for use
const { title, logo } = toRefs(state)
</script>

<style lang="scss">
//vue3.0 过度效果更改  enter-> enter-from   leave-> leave-from
.sidebar-logo-container {
  position: relative;
  width: 50px;
  height: 50px;
  overflow: hidden;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px solid white;
}
</style>
