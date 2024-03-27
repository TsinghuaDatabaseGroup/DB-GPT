<template>
  <div class="columnSC" style="width: 100%">
    <div class="rowBC" style="padding: 20px; width: 100%">
      <div style="font-size: 24px; color: #333333">{{ $t('KnowledgeListTitle') }}</div>
      <el-button size="default" plain type="primary" @click="onCreateKnowledgeClick">{{ $t('KnowledgeCreteButtonTitle') }}</el-button>
    </div>
    <div class="rowSC wrap knowledges-container" style="padding: 10px 20px; width: 100%">
      <div v-for="(item, index) in knowledge.list" :key="index" class="knowledge-container" @click="onKnowledgeClick(item)">
        <div class="rowBC">
          <div class="title rowSC">
            <el-icon style="margin-right: 5px;" size="20" color="var(--el-color-primary)">
              <TakeawayBox/>
            </el-icon>
            <span>{{ item.kb_name }}</span>
          </div>
          <el-tag size="small" style="margin-left: 5px;">{{ item.embed_model }}</el-tag>
        </div>
        <div class="desc">
          {{ item.kb_info }}
        </div>
        <div class="rowSC wrap">
          <div v-for="(vs_item, vs_index) in item.vs_types" :key="vs_index" style="margin-right: 16px">
            <el-tag size="small" style="margin-bottom: 5px">{{ vs_item.vs_type }}</el-tag>
            <span style="color: #333333; margin: 0 2px">/</span>
            <el-tag size="small" style="margin-bottom: 5px">{{vs_item.file_count}} files</el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogCreateFormVisible" title="Creating a knowledge Base" width="800" destroy-on-close>
      <el-form ref="ruleFormRef" :model="createForm" label-width="160">
        <el-form-item label="Name" prop="kb_name" :rules="[{required: true, message: 'Please Input Name', trigger: 'blur'}]">
          <el-input v-model="createForm.kb_name" />
        </el-form-item>
        <el-form-item label="Brief Introduction" prop="kb_info" :rules="[{required: true, message: 'Please Input Brief Introduction', trigger: 'blur'}]">
          <el-input v-model="createForm.kb_info" :rows="2" type="textarea"/>
        </el-form-item>
        <el-form-item label="Embedding Model" prop="model" :rules="[{required: true, message: 'Please Select a Embedding Model', trigger: 'blur, change'}]">
          <el-select v-model="createForm.model" placeholder="Please select a Embedding Model" style="width: 100%">
            <el-option v-for="item in embedList.value" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogCreateFormVisible = false">Cancel</el-button>
          <el-button type="primary" @click="onCreateClick()">
            Create
          </el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts" name="Knowledge">

import {knowledgeListReq, llmModelEmbedModelsReq, createKnowledgeBaseReq} from "@/api/knowledge";
import {ElMessage} from "element-plus";
import { reactive, ref } from 'vue'

const router = useRouter()

const knowledge: Ref<Array<object>>  =  reactive({list: []});

const embedList: Ref<Array<string>> = reactive([])

const ruleFormRef = ref<FormInstance>()

const dialogCreateFormVisible = ref(false)

const createForm = reactive({
  kb_name: '',
  kb_info: '',
  model: 'm3e-base'
})


onMounted(() => {
  getKnowledgeList()
  getEmbedModels()
});

const getKnowledgeList = async () => {
  const res = await knowledgeListReq();
  knowledge.list = mergeSameKb(res.data)
}

const mergeSameKb = (data) => {
  const mergedDataMap = {}
  data.forEach(item => {
    const key = item.kb_name;
    if (!mergedDataMap[key]) {
      mergedDataMap[key] = {
        kb_name: key,
        kb_info: item.kb_info,
        embed_model: item.embed_model,
        create_time: item.create_time,
        vs_types: [{vs_type: item.vs_type, file_count: item.file_count}]
      };
    } else {
      mergedDataMap[key].vs_types.push({vs_type: item.vs_type, file_count: item.file_count});
    }
  });
  return mergedDataMap ? Object.values(mergedDataMap) : [];
}

const getEmbedModels = async () => {
  embedList.value = []
  llmModelEmbedModelsReq().then(res => {
    embedList.value = res.data;
  })
}
const onCreateKnowledgeClick = () => {
  createForm.kb_name = ''
  createForm.kb_info = ''
  createForm.model = 'm3e-base'
  dialogCreateFormVisible.value = true
}

const onKnowledgeClick = (item) => {
  router.push({path: '/knowledge/detail', query: {kb_name: item.kb_name}})
}

const onCreateClick = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      createKnowledgeBaseReq(createForm.kb_name, createForm.kb_info, createForm.model).then(() => {
        dialogCreateFormVisible.value = false
        ElMessage({
          type: 'success',
          message: 'Create Successfully',
        })
        getKnowledgeList()
      })
    } else {
      return false
    }
  })
}


</script>

<style>
.knowledge-container:hover {
  box-shadow: 0 0 5px 5px rgba(0, 0, 0, 0.04);
  border-color: var(--el-color-primary);
}

.knowledges-container {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-gap: 10px;
}
</style>

<style lang="scss">
.knowledge-container {
  flex: 1 1 200px;
  height: 130px;
  border: 1.5px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  background: white;
  display: flex;
  flex-direction: column;
  padding: 10px;

  .title {
    font-size: 16px;
    color: #333333;
  }

  .desc {
    font-size: 14px;
    color: #666666;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    margin: 10px 0;
    flex-shrink: 0;
  }
}


</style>
