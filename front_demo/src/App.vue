<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style lang="scss">

  #app {
    width: 100%;
    height: 100%;
  }

  body .el-table th.gutter {
    display: table-cell !important;
  }

  .el-table th.gutter{
    display: table-cell!important;
  }

</style>
