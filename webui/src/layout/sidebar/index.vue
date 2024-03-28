<template>
  <div id="Sidebar" class="reset-menu-style columnBC relative">

    <div class="columnSC">
      <!--logo-->
      <Logo :collapse="true" style="margin: 20px 0; flex-shrink: 0" />
      <!--router menu-->
      <div class="columnSC" style="width: 100%; height: 100%; overflow-y: scroll; position: relative">
        <sidebar-item v-for="route in allRoutes" :key="route.path" :item="route" :base-path="route.path" :active-path="activeMenu" />
      </div>
    </div>

    <div class="columnCC">
      <div class="columnCC"
           style="margin-bottom: 10px; cursor: pointer; background: RGBA(232, 231, 230, 1.00); padding: 2px; border-radius: 8px"
           @click="onLanguageClick">
        <svg t="1709001310119" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="22841" width="30" height="30"><path
            d="M381.5 483.7c0-53.1 43.2-96.3 96.3-96.3h85v-187c0-9.4-7.6-17-17-17H137.9c-9.4 0-17 7.6-17 17v283.3c0 9.4 7.6 17 17 17h73.6v32.1l64.3-32.1h105.7v-17z" fill="#9ADCCF" p-id="22842"/><path d="M747.7 784h-270c-9.4 0-17-7.6-17-17V483.7c0-9.4 7.6-17 17-17h407.9c9.4 0 17 7.6 17 17V767c0 9.4-7.6 17-17 17H812v32.1L747.7 784z" fill="#FFF370" p-id="22843"/><path d="M341.8 523.4h-56.7c-2.6 0-5.2 0.6-7.6 1.8l-88.7 44.4v-29.2c0-9.4-7.6-17-17-17h-34c-21.9 0-39.7-17.8-39.7-39.7V200.5c0-21.9 17.8-39.7 39.7-39.7h407.9c21.9 0 39.7 17.8 39.7 39.7v147.3c0 9.4 7.6 17 17 17s17-7.6 17-17V200.5c0-40.6-33-73.6-73.6-73.6H137.9c-40.6 0-73.6 33-73.6 73.6v283.3c0 40.6 33 73.6 73.6 73.6h17V597c0 5.9 3 11.4 8.1 14.5 2.7 1.7 5.8 2.5 8.9 2.5 2.6 0 5.2-0.6 7.6-1.8l109.7-54.9h52.6c9.4 0 17-7.6 17-17 0-9.3-7.6-16.9-17-16.9z" fill="#4F3D3B" p-id="22844"/><path d="M885.7 410.1h-65.8c-9.4 0-17 7.6-17 17s7.6 17 17 17h65.8c21.9 0 39.7 17.8 39.7 39.7V767c0 21.9-17.8 39.7-39.7 39.7h-34c-9.4 0-17 7.6-17 17v29.2L746 808.4c-2.4-1.2-5-1.8-7.6-1.8H477.8c-21.9 0-39.7-17.8-39.7-39.7V483.7c0-21.9 17.8-39.7 39.7-39.7h249.3c9.4 0 17-7.6 17-17s-7.6-17-17-17H477.8c-12.9 0-25 3.3-35.5 9.2l-85-180.7c-2.8-6-8.8-9.8-15.4-9.8s-12.6 3.8-15.4 9.8l-90.6 192.6c-4 8.5-0.3 18.6 8.1 22.6 8.5 4 18.6 0.3 22.6-8.1l19.4-41.2h111.7l18.4 39.1c-7.6 11.6-12 25.4-12 40.2V767c0 40.6 33 73.6 73.6 73.6h256.6L844 895.5c2.4 1.2 5 1.8 7.6 1.8 3.1 0 6.2-0.9 8.9-2.5 5-3.1 8.1-8.6 8.1-14.5v-39.7h17c40.6 0 73.6-33 73.6-73.6V483.7c0.1-40.6-32.9-73.6-73.5-73.6z m-583.8-39.7l39.9-84.7 39.9 84.7h-79.8zM358 733.9c-0.2-0.6-0.3-1.1-0.5-1.7-0.2-0.6-0.6-1.1-0.9-1.7-0.2-0.4-0.4-0.8-0.7-1.2-1.2-1.9-2.9-3.5-4.7-4.7-0.4-0.3-0.8-0.4-1.2-0.6-0.6-0.3-1.1-0.7-1.7-0.9-0.5-0.2-1.1-0.3-1.7-0.5-0.5-0.2-1-0.3-1.5-0.4-1.1-0.2-2.2-0.3-3.3-0.3H241c-21.9 0-39.7-17.8-39.7-39.7v-17.1c0-9.4-7.6-17-17-17s-17 7.6-17 17V682c0 40.6 33 73.6 73.6 73.6h59.8L284.5 772c-6.6 6.6-6.6 17.4 0 24 3.3 3.3 7.7 5 12 5s8.7-1.7 12-5l45.3-45.3c0.8-0.8 1.5-1.7 2.1-2.6 0.3-0.4 0.4-0.8 0.7-1.2 0.3-0.6 0.6-1.1 0.9-1.7 0.2-0.5 0.4-1.1 0.5-1.7 0.1-0.5 0.3-1 0.4-1.5 0.4-2.2 0.4-4.5 0-6.7 0-0.5-0.2-1-0.4-1.4z m307.5-511.6c0.2 0.6 0.3 1.1 0.5 1.7 0.2 0.6 0.6 1.1 0.9 1.7 0.2 0.4 0.4 0.8 0.7 1.2 1.2 1.9 2.9 3.5 4.7 4.7 0.4 0.3 0.8 0.4 1.2 0.6 0.6 0.3 1.1 0.7 1.7 0.9 0.5 0.2 1.1 0.3 1.7 0.5 0.5 0.2 1 0.3 1.5 0.4 1.1 0.2 2.2 0.3 3.3 0.3h100.8c21.9 0 39.7 17.8 39.7 39.7v73.6c0 9.4 7.6 17 17 17s17-7.6 17-17V274c0-40.6-33-73.6-73.6-73.6h-59.8l16.3-16.3c6.6-6.6 6.6-17.4 0-24-6.6-6.6-17.4-6.6-24 0l-45.3 45.3c-0.8 0.8-1.5 1.7-2.1 2.6-0.3 0.4-0.4 0.8-0.7 1.2-0.3 0.6-0.6 1.1-0.9 1.7-0.2 0.5-0.4 1.1-0.5 1.7-0.1 0.5-0.3 1-0.4 1.5-0.4 2.2-0.4 4.5 0 6.7 0 0.5 0.2 1 0.3 1.5z" fill="#4F3D3B" p-id="22845"/><path d="M681.7 750c9.4 0 17-7.6 17-17v-45.3H778c9.4 0 17-7.6 17-17V580c0-9.4-7.6-17-17-17h-79.3v-45.3c0-9.4-7.6-17-17-17s-17 7.6-17 17V563h-79.3c-9.4 0-17 7.6-17 17v90.6c0 9.4 7.6 17 17 17h79.3V733c0 9.4 7.6 17 17 17z m17-153H761v56.7h-62.3V597z m-96.3 56.7V597h62.3v56.7h-62.3z" fill="#4F3D3B" p-id="22846"/></svg>      </div>
      <div class="columnCC" style="margin-bottom: 20px; cursor: pointer" @click="onThemeClick">
        <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="14888" width="40"
             height="40">
          <path d="M298.35 84.69h427.3a213.65 213.65 0 0 1 213.66 213.66v427.3a213.65 213.65 0 0 1-213.66 213.66H298.34A213.65 213.65 0 0 1 84.69 725.66V298.35A213.66 213.66 0 0 1 298.35 84.69z" fill="#E8E7E6" p-id="14889"/><path d="M792 504.56l-1.34 0.05C777.09 368.79 662.9 262.74 524 262.74c-144.77 0-262.71 115.19-267.82 259.21h23.91l-24 0.81c-3.76 125 67.29 236.09 201.55 273s112.74-61.85 100.78-69.09-20.39-26.83-9.83-49.35 19.64-21.31 68.82-22.21C750.85 657.28 782.39 562 789.75 522h2.06c-0.12-3.29-0.31-6.57-0.54-9.83 0.58-4.83 0.73-7.61 0.73-7.61z m-434 29.65a48.1 48.1 0 1 1 47.84-48.1 48 48 0 0 1-47.84 48.1z m88.6-116.07a48 48 0 1 1 47.95-48 48 48 0 0 1-47.93 48z m150 2.53a48.1 48.1 0 1 1 47.85-48.1 48 48 0 0 1-47.85 48.1z m93.26 113.54a48.1 48.1 0 1 1 47.95-48.1 48 48 0 0 1-47.95 48.1z" fill="#DD4F47" p-id="14890"/></svg>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia/dist/pinia'
import { useRoute } from 'vue-router'
import Logo from './Logo.vue'
import SidebarItem from './SidebarItem.vue'
import { useBasicStore } from '@/store/basic'
const { allRoutes } = storeToRefs(useBasicStore())
const routeInstance = useRoute()
let useConfigStore = reactive({})

const themeList = ['lighting-theme', 'china-red']

setTimeout(() => {
  import('@/store/config').then((res) => {
    useConfigStore = res.useConfigStore
  })
}, 300)

const activeMenu = computed(() => {
  const { meta, path } = routeInstance
  // if set path, the sidebar will highlight the path you set
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})

const onLanguageClick = () => {
  const { language, setLanguage } = useConfigStore()
  setLanguage(language === 'zh' ? 'en' : 'zh')
}
const onThemeClick = () => {
  const { theme, setTheme } = useConfigStore()
  setTheme(themeList[(themeList.indexOf(theme) + 1) % themeList.length])
  console.log('change theme:', theme)
}

</script>
<style lang="scss">
//fix open the item style issue
.el-menu-vertical {
  width: var(--side-bar-width);
}
.reset-menu-style {
  border-right: 1px solid var(--side-bar-border-right-color);
}
</style>
