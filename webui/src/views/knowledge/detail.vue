<template>
  <div style="height: calc(100vh - 30px)">
    <el-container style="height: 100%">
      <el-aside width="200px" style="border-right: 1px solid var(--border-color); height: 100%;">
        <div class="columnSS" style="width: 100%; padding: 10px;">
          <div class="rowSC">
            <el-button icon="ArrowLeftBold" type="primary" plain circle size="default" @click="routerBack()"/>
            <span style="font-weight: bold; font-size: 20px; margin-left: 10px">{{ $route.query.kb_name }}</span>
          </div>
          <div class="columnSS" style="width: 100%; margin-top: 20px">
            <div :class="`rowSC menu-item ${activeIndex === 'dataset' ? ' active' : ''}`" @click="onMenuClick('dataset')">
              <el-icon>
                <Document/>
              </el-icon>
              <span>数据集</span>
            </div>
            <div :class="`rowSC menu-item ${activeIndex === 'search' ? ' active' : ''}`" @click="onMenuClick('search')">
              <el-icon>
                <Search/>
              </el-icon>
              <span>搜索测试</span>
            </div>
            <div :class="`rowSC menu-item ${activeIndex === 'setting' ? ' active' : ''}`" @click="onMenuClick('setting')">
              <el-icon>
                <Setting/>
              </el-icon>
              <span>配置</span>
            </div>
          </div>
        </div>
      </el-aside>
      <el-main>
        <div v-if="activeIndex === 'dataset'" class="columnSC">
          <div class="rowBC upload-container" style="">
            <el-upload
                ref="upload"
                class="upload"
                :limit="1"
                action=""
                :http-request="uploadFile"
                :on-exceed="handleExceed"
                :auto-upload="false"
            >
              <template #trigger>
                <el-button size="default" type="primary">Select File</el-button>
              </template>
              <template #tip>
                <div class="el-upload__tip">
                  Limit 1 file, new file will cover the old file, Only HTML, MD, JSON, JSONL, CSV, PDF, PNG, JPG, JPEG, BMP, EML, MSG, EPUB, XLSX, XLSD, IPYNB,
                  ODT, PY, RST, RTF, SRT, TOML, TSV, DOCX, DOC, XML, PPT, PPTX, TXT, HTM
                </div>
              </template>
            </el-upload>
            <el-button size="default" type="success" @click="onUploadDocsClick">
              UPLOAD
            </el-button>
          </div>
          <el-table :data="fileList.value" style="width: 100%; border-radius: 10px;" height="calc(100vh - 220px)">
            <el-table-column prop="No" label="No" width="60" align="center"/>
            <el-table-column prop="file_name" label="File Name" header-align="center"/>
            <el-table-column prop="docs_count" label="Data Count" width="120" align="center"/>
            <el-table-column fixed="right" label="Operations" width="170" align="center">
              <template #default="scope">
                <el-button text type="primary" size="small" @click="onHandleFileReviewClick(scope.row)">Review</el-button>
                <el-button text type="primary" size="small" @click="onHandleFileDeleteClick(scope.row)">Delete</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-if="activeIndex === 'search'">
          <div class="rowBC" style="margin-bottom: 20px">
            <el-input v-model="searchValue" :rows="2" type="textarea" placeholder="Search" style="width: calc(100% - 100px)"/>
            <el-button :disabled="searchValue.value" type="primary" @click="onSearchClick">Search</el-button>
          </div>
          <el-table :data="searchResult.value" style="width: 100%; border-radius: 10px;" height="calc(100vh - 140px)">
            <el-table-column prop="page_content" label="page content" header-align="center"/>
            <el-table-column prop="metadata.source" label="source" header-align="center"/>
          </el-table>
        </div>
        <div v-if="activeIndex === 'setting'">
          <div class="relative columnSS">
            <div
class="columnSS"
                 style="padding: 20px; border-radius: 10px; margin-top: 20px; width: calc(100% - 10px)">
              <div class="rowSC" style="width: 100%;">
                <span style="color: #000000; width: 180px; text-align: left; font-size: 16px; flex-shrink: 0">Name</span>
                <span style="color: #333333;">{{ editForm.kb_name }}</span>
              </div>

              <div class="rowSC" style="width: 100%; margin-top: 20px;">
                <span style="color: #000000; width: 180px; text-align: left; font-size: 16px; flex-shrink: 0">Brief Introduction</span>
                <el-input v-model="editForm.kb_info" :rows="2" type="textarea"/>
              </div>

              <div class="rowSC" style="width: 100%; margin-top: 20px;">
                <span style="color: #000000; width: 180px; text-align: left; font-size: 16px; flex-shrink: 0">Embedding Model</span>
                <span style="color: #333333;">{{ editForm.embed_model }}</span>
              </div>
            </div>

            <div class="rowSC" style="margin-left: 20px; margin-top: 20px">
              <el-button size="default" type="primary" @click="onHandleSaveClick">Save</el-button>
              <el-button style="margin-left: 10px" :icon="Delete" size="small" circle @click="onHandleDeleteClick" />
            </div>

          </div>
        </div>
      </el-main>
    </el-container>
    <el-drawer
        v-model="reviewDrawer"
        :title="reviewDrawerTitle"
        class="dataset-detail-drawer"
        direction="rtl"
        size="calc(100% - 300px)"
        :append-to-body="true"
    >
      <ul v-loading="reviewDrawerLoading" class="infinite-list columnSS" style="width: 100%">
        <li v-for="(item, index) in fileSplitContents.value" :key="index" class="infinite-list-item" style="width: calc(100% - 20px)">
          <div class="columnSS" style="width: 100%;">
            <div class="rowBC infinite-list-item-header">
              <div style="color: var(--el-color-primary);">#{{ index + 1 }}</div>
              <div class="rowSC" style="color: #666666; margin-left: 10px">
                <svg t="1708530334824" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="15983" width="16" height="16"><path d="M854.013267 0.001792A170.751402 170.751402 0 0 1 1023.996672 170.753194v682.493612A170.751402 170.751402 0 0 1 854.013267 1023.998208H171.263657A170.495403 170.495403 0 0 1 0.000256 853.246806V170.753194A170.495403 170.495403 0 0 1 171.263657 0.001792zM363.006985 835.070869a15.615945 15.615945 0 0 0-15.615945 15.615946v13.823951a15.359946 15.359946 0 0 0 4.863983 11.263961 14.847948 14.847948 0 0 0 11.51996 4.351985l82.68771-3.839987c27.903902 0 51.199821-1.535995 68.095762-1.535995 25.59991 0 70.143754 1.535995 136.959521 4.607984h22.015923a15.615945 15.615945 0 0 0 15.615945-15.615945v-14.079951a15.615945 15.615945 0 0 0-15.615945-15.615945h-2.303992a143.103499 143.103499 0 0 1-45.82384-5.63198 42.495851 42.495851 0 0 1-24.063916-18.431936 127.999552 127.999552 0 0 1-9.727966-40.191859C588.798195 752.639158 588.798195 721.407267 588.798195 676.351425v-95.487666c0-46.591837 0-108.031622 2.559991-329.214848a15.615945 15.615945 0 0 1 15.615946-15.615945h74.23974c51.199821 0 87.039695 7.167975 104.703633 21.759924a153.599462 153.599462 0 0 1 31.48789 70.399753 15.871944 15.871944 0 0 0 17.663938 11.263961l16.895941-2.559991a15.615945 15.615945 0 0 0 13.055954-17.407939 1800.953697 1800.953697 0 0 1-7.935972-75.007738 981.500565 981.500565 0 0 1-3.327988-82.431711 12.543956 12.543956 0 0 0-4.863983-8.447971 12.287957 12.287957 0 0 0-10.495963-2.559991 236.799171 236.799171 0 0 1-39.167863 6.143979c-25.59991 2.047993-68.351761 2.81599-131.071542 2.81599h-307.198924c-55.807805 0-95.487666 0-119.039584-2.81599a278.527025 278.527025 0 0 1-36.863871-5.375981 15.103947 15.103947 0 0 0-12.799955 2.81599 16.639942 16.639942 0 0 0-6.143978 11.519959c-2.047993 31.231891-4.351985 55.551806-6.655977 72.703746s-7.423974 45.311841-14.847948 81.407715a15.871944 15.871944 0 0 0 14.591949 17.663938l18.687934 3.839987a15.615945 15.615945 0 0 0 18.175937-10.495963 161.535435 161.535435 0 0 1 35.327876-72.703746c19.711931-15.103947 56.319803-22.527921 109.823616-22.527921h71.935748a15.871944 15.871944 0 0 1 11.007961 4.607984 15.359946 15.359946 0 0 1 4.607984 11.007961v276.223033c0 99.327652 0 167.423414-2.047993 204.799284a291.838979 291.838979 0 0 1-7.167974 69.375757 45.311841 45.311841 0 0 1-23.295919 25.59991 126.463557 126.463557 0 0 1-51.199821 7.423974z m0 0" fill="#13227a" p-id="15984"/></svg>
                <span style="margin-left: 5px">{{ item.length }}</span>
              </div>
            </div>
            <div class="infinite-list-item-content" style="width: 100%">
              {{ item }}
            </div>
          </div>
        </li>
      </ul>
    </el-drawer>
  </div>
</template>

<script setup lang="ts" name="KnowledgeDetail">
import {knowledgeDeleteDocsReq, knowledgeFileDetailsReq, knowledgeFileSplitContentReq,
  knowledgeSearchDocsReq, knowledgeUploadDocsReq, knowledgeBaseDetailReq, knowledgeBaseUpdateInfoReq, knowledgeBaseDeleteReq } from
      "@/api/knowledge";
import { ElMessage, ElMessageBox, genFileId } from 'element-plus'
import { reactive, ref } from 'vue'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'

// 获取store和router
import {Delete, Document, Search, Setting} from "@element-plus/icons-vue";

const router = useRouter()

const route = useRoute()

const activeIndex: Ref<string> = ref('dataset')

const fileList: Ref<Array<object>> = reactive([])

const reviewDrawer: Ref<boolean> = ref(false)

const reviewDrawerLoading: Ref<boolean> = ref(true)

const reviewDrawerTitle: Ref<string> = ref('')

const fileSplitContents: Ref<Array<string>> = reactive([])

const upload = ref<UploadInstance>()

const searchValue: Ref<string> = ref('')

const searchResult: Ref<Array<object>> = reactive([])

const editForm = reactive({
  kb_name: '',
  kb_info: '',
  embed_model: ''
})


watch(
    () => activeIndex.value,
    (newValue, oldValue) => {
      console.log('activeIndex', newValue, oldValue)
      if (newValue === 'setting') {
        getKnowledgeBaseDetail()
      }
    },
    {immediate: true}
)


onMounted(async () => {
  activeIndex.value = route.query.activeIndex || 'dataset'
  getFileDetail()
})


const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}

const getFileDetail = () => {
  fileList.value = []
  knowledgeFileDetailsReq(route.query.kb_name).then(res => {
    fileList.value = res.data.map(item => {
      let fileName = item.file_name;
      fileName = fileName.slice(Math.max(0, fileName.lastIndexOf('/') + 1));
      return {...item, file_name: fileName, file_path: item.file_name}
    });
  })
}

const getKnowledgeBaseDetail = () => {
  fileList.value = []
  knowledgeBaseDetailReq(route.query.kb_name).then(res => {
    editForm.kb_name = res.data.kb_name
    editForm.kb_info = res.data.kb_info
    editForm.embed_model = res.data.embed_model
  })
}


const getFileSplitContent = (fileName) => {
  knowledgeFileSplitContentReq(route.query.kb_name, fileName).then(res => {
    if (!res.data[0] && !res.data[0]['data'] && !res.data[0]['data'][0] && !res.data[0]['data'][0]['contents']) {
      return
    }
    fileSplitContents.value = res.data[0]['data'][0]['contents'] || []
  }).finally(() => {
    reviewDrawerLoading.value = false
  })
}

const deleteDocs = (fileName) => {
  knowledgeDeleteDocsReq(route.query.kb_name, fileName).then(() => {
    ElMessage({
      type: 'success',
      message: 'Delete completed',
    })
    getFileDetail()
  }).finally(() => {

  })
}

const onHandleSaveClick = () => {
  knowledgeBaseUpdateInfoReq(route.query.kb_name, editForm.kb_info).then(() => {
    ElMessage({
      type: 'success',
      message: 'Update completed',
    })
  })
}

const onSearchClick = () => {
  if (!searchValue.value) {
    return
  }
  searchResult.value = []
  knowledgeSearchDocsReq(route.query.kb_name, searchValue.value).then(res => {
    searchResult.value = res.data
  })
}

const onHandleDeleteClick = () => {
  ElMessageBox.confirm(
      'Will delete the Knowledge Base. Continue?',
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
  )
      .then(() => {
        knowledgeBaseDeleteReq(route.query.kb_name).then(() => {
          ElMessage({
            type: 'success',
            message: 'Delete completed',
          })
          routerBack()
        })
      }).catch(() => {})
}

const onUploadDocsClick = () => {
  upload.value!.submit()
}

const uploadFile = (files) => {
  console.log(files)
  knowledgeUploadDocsReq(route.query.kb_name, files.file).then(() => {
    ElMessage({
      type: 'success',
      message: 'Upload Docs Completed',
    })
    getFileDetail()
  }).finally(() => {

  })
}

const onMenuClick = (index) => {
  activeIndex.value = index
}

const onHandleFileReviewClick = (file) => {
  console.log('file:', file)
  fileSplitContents.value = []
  reviewDrawerTitle.value = file.file_name
  reviewDrawer.value = true
  reviewDrawerLoading.value = true
  getFileSplitContent(file.file_name)
}

const onHandleFileDeleteClick = (file) => {
  console.log('file:', file)
  ElMessageBox.confirm(
      'Will permanently delete the file. Continue?',
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
  )
      .then(() => {
        deleteDocs(file.file_path)
      }).catch(() => {})
}

const routerBack = () => {
  router.back()
}

</script>

<style>
.dataset-detail-drawer {
  border-top-left-radius: 10px;
  border-bottom-left-radius: 10px;
}
.dataset-detail-drawer > .el-drawer__header {
  margin-bottom: 0!important;
}
.upload-container {
  width: 100%;
  height: 140px;
  overflow-y: scroll;
  background-color: white;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
.upload {
  width: calc(100% - 120px);
}
.el-descriptions__body {
  background-color: transparent!important;
}
</style>

<style scoped lang="scss">
.menu-item {
  width: 100%;
  margin-bottom: 10px;
  padding: 10px 10px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid var(--el-color-primary);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);

  .el-icon {
    margin-right: 10px;
  }

  &:hover {
    background: var(--el-color-primary);
    color: white;
  }

  &.active {
    background: var(--el-color-primary);
    color: white;
  }
}

.infinite-list {
  height: 100%;
  padding: 0;
  margin: 0;
  list-style: none;
  overflow: auto;
  .infinite-list-item {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 10px;
    .infinite-list-item-header {
      margin-bottom: 10px;
      width: 100%;
    }
    .infinite-list-item-content {
      white-space: pre-wrap;
      color: var(--el-color-primary);
      background: var(--el-color-primary-light-9);
      border-radius: 4px;
      padding: 10px;
      height: auto;
    }
  }
}

</style>
