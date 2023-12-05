<template>
  <div class="c-flex-column c-align-items-center c-justify-content-between">
    <div>
      <logo v-if="showLogo" :collapse="isCollapse" />
      <el-scrollbar wrap-class="scrollbar-wrapper">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :background-color="variables.menuBg"
          :text-color="variables.menuText"
          :unique-opened="false"
          :default-openeds="['/','/index']"
          :active-text-color="variables.menuActiveText"
          :collapse-transition="true"
          mode="vertical"
        >
          <sidebar-item v-for="route in routes" :key="route.path" :item="route" :base-path="route.path" />
        </el-menu>
      </el-scrollbar>
    </div>
    <div class="c-flex-column c-align-items-center" style="flex-shrink: 0">
      <div class="bottom-logo-container c-align-items-center c-flex-column" @click="onModelClick('GPT4-0613')">
        <img src="@/assets/openai_logo.png" style="width: 30px; height: 30px;">
        <span style="font-size: 12px; color: #333333;">OpenAI</span>
        <span v-if="model === 'GPT4-0613'" style="padding: 4px 8px; background: #41b584; border-radius: 4px; margin-top: 4px" />
      </div>
      <div
        class="bottom-logo-container c-align-items-center c-flex-column"
        @click="onModelClick('Llama2-13b')"
      >
        <img src="@/assets/llama_logo.png" style="width: 30px; height: 30px;">
        <span style="font-size: 12px; color: #333333;">Llama</span>
        <span v-if="model === 'Llama2-13b'" style="padding: 4px 8px; background: #41b584; border-radius: 4px; margin-top: 4px" />
      </div>
      <div
        class="bottom-logo-container c-align-items-center c-flex-column"
        @click="onModelClick('CodeLlama2-13b')"
      >
        <img src="@/assets/codellama_logo.png" style="width: 30px; height: 30px;">
        <span style="font-size: 12px; color: #333333;">CodeLlama</span>
        <span v-if="model === 'CodeLlama2-13b'" style="padding: 4px 8px; background: #41b584; border-radius: 4px; margin-top: 4px" />
      </div>
      <div
        class="bottom-logo-container c-align-items-center c-flex-column"
        @click="onModelClick('BaiChuan-13b')"
      >
        <img src="@/assets/baichuan_logo.png" style="width: 30px; height: 30px;">
        <span style="font-size: 12px; color: #333333;">BaiChuan</span>
        <span v-if="model === 'BaiChuan-13b'" style="padding: 4px 8px; background: #41b584; border-radius: 4px; margin-top: 4px" />
      </div>
      <div class="bottom-logo-container c-justify-content-center c-flex-row" @click="onEnClick">
        <img src="@/assets/ch_to_en.png" style="width: 30px; height: 30px;">
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Logo from './Logo'
import SidebarItem from './SidebarItem'
import variables from '@/styles/variables.scss'

export default {
  components: { SidebarItem, Logo },
  computed: {
    ...mapGetters([
      'sidebar'
    ]),
    routes() {
      return this.$router.options.routes
    },
    activeMenu() {
      const route = this.$route
      const { meta, path } = route
      // if set path, the sidebar will highlight the path you set
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    },
    showLogo() {
      return this.$store.state.settings.sidebarLogo
    },
    variables() {
      return variables
    },
    isCollapse() {
      return !this.sidebar.opened
    },
    model() {
      return this.$store.getters.model
    }
  },
  methods: {
    onModelClick(model) {
      this.$store.dispatch('settings/model', model)
    },
    onEnClick() {
      this.$i18n.locale = this.$i18n.locale === 'en' ? 'zh' : 'en'
      localStorage.setItem('LanguageSwitching', this.$i18n.locale)
    }
  }
}
</script>

<style>
.bottom-logo-container {
  cursor: pointer;
  width: 100%;
  margin-bottom: 30px;
}

</style>
