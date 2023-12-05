<template>
  <div :class="classObj" class="app-wrapper">
    <template v-if="!($device.mobile || $device.ipad)">
      <sidebar class="sidebar-container" />
      <div
        class="main-container"
        style="width: calc(100vw - 84px); margin-left: 84px; padding: 0 0; height: 100%; overflow: hidden;"
      >
        <app-main style="width: 100%" />
      </div>
    </template>
    <template v-else>
      <div class="exception-mobile c-flex-column c-justify-content-center c-align-items-center" style="background: RGBA(240, 170, 150, 1.00)">
        <img src="@/assets/only_desk.png" style="width: 80%; border-radius: 8px; margin-bottom: 20px">
        <span
          style="color: #ffffff; width: 80%; font-size: 16px; text-align: left; line-height: 2; font-weight: bolder;"
        >
          Please visit and try out on PC. <br> We will adapt the mobile page soon.<br> Thanks for your support! ❤️️❤️️</span>
      </div>
    </template>
  </div>
</template>

<script>
import { Sidebar, AppMain } from './components'
import ResizeMixin from './mixin/ResizeHandler'

export default {
  name: 'Layout',
  components: {
    Sidebar,
    AppMain
  },
  mixins: [ResizeMixin],
  computed: {
    sidebar() {
      return this.$store.state.app.sidebar
    },
    device() {
      return this.$store.state.app.device
    },
    fixedHeader() {
      return this.$store.state.settings.fixedHeader
    },
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened,
        withoutAnimation: this.sidebar.withoutAnimation,
        mobile: this.device === 'mobile'
      }
    }
  },
  mounted() {
    console.log('=========:', this.$device)
  },
  methods: {
    handleClickOutside() {
      this.$store.dispatch('app/closeSideBar', { withoutAnimation: false })
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/mixin.scss";
@import "~@/styles/variables.scss";

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100vh;
  width: 100vw;
  background: RGBA(245, 245, 245, 1.00);

  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}

.drawer-bg {
  background: #ffffff;
  opacity: 1;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: calc(100% - 74px);
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: calc(100% - 74px)
}

.mobile .fixed-header {
  width: 100%;
}

.exception-mobile {
  width: 100vw;
  height: 100vh;
  text-align: center;
  background: white;
}
</style>
