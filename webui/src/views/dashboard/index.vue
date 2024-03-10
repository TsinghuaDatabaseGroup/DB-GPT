<template>
  <div class="scroll-y">
    <div class="mt-10px mb-10px font-bold">switch theme</div>
    <el-button @click="setTheme('base-theme')">base-theme(default)</el-button>
    <el-button @click="setTheme('lighting-theme')">lighting-theme</el-button>
    <el-button @click="setTheme('china-red')">china-red(default)</el-button>
    <el-button @click="setTheme('dark')">dark-theme</el-button>

    <div class="mt-10px mb-10px font-bold">switch size</div>
    <el-button @click="setSize('large')">large</el-button>
    <el-button @click="setSize('default')">default</el-button>
    <el-button @click="setSize('small')">small</el-button>

    <div class="mt-10px mb-10px font-bold">switch language</div>
    <el-button @click="changeLanguage('en')">en</el-button>
    <el-button @click="changeLanguage('zh')">zh</el-button>

    <!--example components -->
    <div class="mb-10px font-bold mt-20px">Button Group</div>
    <el-button type="primary" @click="count++">count is: {{ count }}</el-button>
    <el-button type="success" @click="count++">count is: {{ count }}</el-button>
    <el-button type="warning" @click="count++">count is: {{ count }}</el-button>
    <el-button type="danger" @click="count++">count is: {{ count }}</el-button>
    <el-button type="info" @click="count++">count is: {{ count }}</el-button>

    <div class="mt-30px font-bold mb-10px">unocss using</div>
    <div class="mb-40px w-900px h-10px text-16px">
      <div>
        you can look
        <el-link class="text-red" href="https://uno.antfu.me/" target="_blank">https://uno.antfu.me/</el-link>
        to search you need such as "margin-left:10px" and then get the sortcut(ml-10px)
      </div>
    </div>

    <div class="mt-30px font-bold mb-10px">global var</div>
    {{ showObj }}

    <div class="mt-20px">
      <el-button @click="sendReq">发送请求测试(network->slow 3g)</el-button>
      <el-button @click="cancelReq">cancelReq</el-button>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useConfigStore } from '@/store/config'

const { setTheme, theme, setSize, size, setLanguage } = useConfigStore()
const route = useRoute()
const changeLanguage = (langParam) => {
  setLanguage(langParam, route.meta?.title)
}
const count = ref(0)
const showObj = ref(GLOBAL_VAR)

//send req test
const sendReq = () => {
  const reqConfig = {
    url: '/integration-front/errorCollection/selectPage',
    method: 'get',
    reqLoading: false
  }
  axiosReq(reqConfig)
}
//cancel req
const { axiosPromiseArr } = useBasicStore()
const cancelReq = () => {
  //cancel all req when page switch
  if (axiosPromiseArr.length) {
    axiosPromiseArr.forEach((ele, ind) => {
      ele.cancel()
      axiosPromiseArr.splice(ind, 1)
    })
  }
}
</script>
