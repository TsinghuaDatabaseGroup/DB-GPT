<template>
  <div class="relative rowSC chat-container">
    <el-container style="height: 100%">
      <el-aside v-if="false" width="220px" style="border-right: 1px solid var(--border-color); height: 100%; padding: 20px">
        <div>
          <span style="color: #333333; font-weight: bold; margin-bottom: 10px">LLM Model:</span>
          <el-select
              v-model="llmModel"
              class="database-select"
              placeholder="Select"
              style="width: 180px"
              size="default"
          >
            <el-option
                v-for="item in modelList"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>
        </div>
        <div class="columnBC" style="height: calc(100% - 60px);">
          <div class="columnSS" style="width: 100%">
            <span style="color: #333333; font-weight: bold; margin: 10px 0">Database:</span>
            <div class="columnSS" v-if="databaseOptionList.length > 0" style="width: 100%; ">
              <div
                  v-for="(item, index) in databaseOptionList" :key="index"
                  :class="`rowSC database-select-item ${databaseSelect.host === item.host && databaseSelect.database === item.database ? ' active' : ''}`"
                  @click="onDatabaseClick(item)">
                <el-popover
                    ref="popover"
                    placement="right"
                    effect="dark"
                    trigger="hover"
                >
                  <div class="rowBC" style="margin: 0 20px">
                    <el-button type="warning" circle @click.stop="onEditDatabaseOptionClick(item)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button type="danger" circle @click.stop="onDeleteDatabaseOptionClick(item)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <template #reference>
                    <el-text style="width: 160px; color: #333333;" size="default" truncated>
                      {{ item.host }} / {{ item.database }}
                    </el-text>
                  </template>
                </el-popover>
              </div>
            </div>
            <el-empty v-else description="No Database" :image-size="200" />
          </div>
          <el-button size="large" style="border-radius: 20px!important;" plain @click="onAddDatabaseOptionClick">
            Add an database
          </el-button>
        </div>
      </el-aside>
      <el-main>
        <div class="layout-flow">
          <VueFlow style="width: 100%; height: 300px" :default-viewport="{ zoom: 0.5 }" :max-zoom="4" :min-zoom="1" :nodes="nodes" :edges="edges"
                   @nodes-initialized="layoutGraph('LR')">
            <template #node-process="props">
              <el-popover
                  placement="right-start"
                  :width="800"
                  trigger="click"
              >
                <span>{{ JSON.stringify(props.data) }}</span>
                <dataflow-data-show :message="currentNodeMessage" :is-last="false"/>
                <template #reference>
                  <ProcessNode
                      :data="props.data"
                      :source-position="props.sourcePosition" :target-position="props.targetPosition" />
                </template>
              </el-popover>
            </template>

            <template #edge-animation="edgeProps">
              <AnimationEdge
                  :id="edgeProps.id"
                  :source="edgeProps.source"
                  :target="edgeProps.target"
                  :source-x="edgeProps.sourceX"
                  :source-y="edgeProps.sourceY"
                  :targetX="edgeProps.targetX"
                  :targetY="edgeProps.targetY"
                  :source-position="edgeProps.sourcePosition"
                  :target-position="edgeProps.targetPosition"
              />
            </template>

            <Background style="width: 100%; height: 300px" />

            <Panel class="process-panel" position="top-right">
              <el-popover
                  placement="bottom-start"
                  effect="light"
                  width="auto"
                  trigger="hover"
              >
                <div class="rowBC" style="width: 100%;">
                  <div class="columnBC shadow add-container" style="margin-right: 10px;" @click="onAddDatabaseOptionClick">
                    <el-icon size="24"><Coin /></el-icon>
                    <span style="margin-top: 10px">添加数据库</span>
                  </div>

                  <div class="columnBC shadow add-container">
                    <el-icon size="24"><List /></el-icon>
                    <span style="margin-top: 10px">添加文件</span>
                  </div>

                </div>
                <template #reference>
                  <el-button size="default" type="success" circle>
                    <el-icon color="#ffffff" size="24"><Plus /></el-icon>
                  </el-button>
                </template>
              </el-popover>
            </Panel>

          </VueFlow>
        </div>
        <div ref="messagesScrollDiv" class="messages-container">
          <database-chat-item
              v-for="(item, index) in messageList" :key="index" :message="item"
              :is-last="index === messageList.length - 1"/>
        </div>
        <BottomInputContainer style="width: 100%" placeholder="请输入你的需求，例如：查看订单在所有国家的分布情况" @send-click="onSendClick" >
          <template #left>
            <div style="margin-right: 10px; cursor: pointer" @click="onPromptConfigClick">
              <svg t="1709047097752" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="12784" width="26" height="26"><path
                  d="M816.832 787.712v63.488a44.8 44.8 0 0 1-89.6 0v-63.488c14.4 3.712 29.248 6.208 44.8 6.208 15.552 0 30.4-2.496 44.8-6.208zM556.8 592.832v258.304a44.8 44.8 0 1 1-89.6 0V592.768c14.4 3.648 29.248 6.144 44.8 6.144 15.552 0 30.4-2.496 44.8-6.144z m-260.032 194.88v63.488a44.8 44.8 0 0 1-89.6 0v-63.488c14.4 3.712 29.248 6.208 44.8 6.208 15.552 0 30.4-2.496 44.8-6.208z m-44.8-302.208a123.968 123.968 0 1 1 0 247.936 123.968 123.968 0 0 1 0-247.936z m520.064 0a123.968 123.968 0 1 1 0 247.936 123.968 123.968 0 0 1 0-247.936z m-520.064 89.6a34.432 34.432 0 1 0 0.064 68.864 34.432 34.432 0 0 0-0.064-68.864z m520.064 0a34.432 34.432 0 1 0 0.064 68.864 34.432 34.432 0 0 0-0.064-68.864zM512 290.56a123.968 123.968 0 1 1 0 247.936A123.968 123.968 0 0 1 512 290.56z m0 89.6a34.496 34.496 0 0 0 0 68.736 34.432 34.432 0 0 0 0-68.8zM251.968 128a44.8 44.8 0 0 1 44.8 44.8v258.432a181.44 181.44 0 0 0-44.8-6.144c-15.552 0-30.4 2.496-44.8 6.144V172.8a44.8 44.8 0 0 1 44.8-44.864z m520.064 0a44.8 44.8 0 0 1 44.8 44.8v258.432a181.44 181.44 0 0 0-44.8-6.144c-15.552 0-30.4 2.496-44.8 6.144V172.8a44.8 44.8 0 0 1 44.8-44.864zM512 128a44.8 44.8 0 0 1 44.8 44.8v63.36a181.44 181.44 0 0 0-44.8-6.08c-15.552 0-30.4 2.496-44.8 6.144V172.8A44.8 44.8 0 0 1 512 128z" fill="#1296db" p-id="12785"/></svg>
            </div>
          </template>
        </BottomInputContainer>
      </el-main>
    </el-container>

    <el-dialog v-model="dialogEditDatabaseVisible" title="Edit Database" width="800" destroy-on-close :close-on-click-modal="false">
      <el-form ref="ruleFormRef" size="default" :model="editDatabaseForm" label-width="80">
        <el-form-item label="host" prop="host" :rules="[{required: true, message: 'Please Input host', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.host" size="default" />
        </el-form-item>
        <el-form-item label="user" prop="user" :rules="[{required: true, message: 'Please Input user', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.user" size="default" />
        </el-form-item>
        <el-form-item label="password" prop="password" :rules="[{required: true, message: 'Please Input password', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.password" size="default" show-password />
        </el-form-item>
        <el-form-item label="database" prop="database" :rules="[{required: true, message: 'Please Input database', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.database" size="default" />
        </el-form-item>
        <el-form-item label="port" prop="port" :rules="[{required: true, message: 'Please Input port', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.port" size="default" />
        </el-form-item>

        <el-form-item label="Intro" prop="intro" :rules="[{required: true, message: 'Please Input intro', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.intro" placeholder="请输入该数据库的相关介绍" type="textarea" :rows="2" size="default" />
        </el-form-item>

        <el-form-item label="Prompt" prop="prompt" :rules="[{required: true, message: 'Please Input prompt', trigger: 'blur'}]">
          <el-input v-model="editDatabaseForm.prompt" placeholder="请输入获取该数据库数据的提示词" type="textarea" :rows="2" size="default" />
        </el-form-item>

      </el-form>

      <div class="rowSC">
        <el-button plain size="default" type="primary" @click="onDatabaseDDLClick">
          <el-icon style="margin-right: 10px"><Link /></el-icon>
          Test Connection and Get DDL
        </el-button>
      </div>

      <div v-if="editDatabaseForm.ddl && editDatabaseForm.ddl.length > 0" class="rowSC wrap" style="margin-top: 20px">
        <el-tabs
            v-model="ddlActiveName"
            style="width: 100%"
        >
          <el-tab-pane v-for="(item, index) in editDatabaseForm.ddl" :key="index" :label="item.table" :name="index.toString()">
            <div>
              <el-input
                  v-model="item.ddl"
                  type="textarea"
                  :rows="10"
                  placeholder="DDL"
                  :disabled="true"
                  style="width: 100%"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template v-if="editDatabaseForm.ddl && editDatabaseForm.ddl.length > 0" #footer>
        <div class="dialog-footer">
          <el-button type="primary" size="default" @click="onCreateDatabaseClick()">
            Save to localStorage
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="dialogPromptConfigVisible" title="Database Prompt Config" width="80%" destroy-on-close :close-on-click-modal="false">
      <el-form ref="promptFormRef" size="default" :model="promptConfigForm" label-width="150">
        <el-form-item label="Visulization Prompt" prop="visulization_prompt" :rules="[{required: true, message: 'Please Input Visulization Prompt', trigger: 'blur'}]">
          <el-input v-model="promptConfigForm.visulization_prompt" type="textarea" :rows="10" size="default" />
        </el-form-item>
        <el-form-item label="Query Prompt" prop="query_prompt" :rules="[{required: true, message: 'Please Input Query Prompt', trigger: 'blur'}]">
          <el-input v-model="promptConfigForm.query_prompt" type="textarea" :rows="10" size="default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" size="default" @click="onSavePromptClick()">
            Save to localStorage
          </el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts" name="Index">

import {chatReq, dbDdlInfoReq, dbExecuteSqlReq, dbGenerateSqlReq, llmModelListModelsReq} from "@/api/knowledge";
import DatabaseChatItem from "@/components/DatabaseChatItem.vue";
import DataflowDataShow from "@/components/DataflowDataShow.vue";
import BottomInputContainer from "@/components/BottomInputContainer.vue";
import {ElMessage, ElMessageBox} from "element-plus";
import { Panel, VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import ProcessNode from './ProcessNode.vue'
import AnimationEdge from './AnimationEdge.vue'
import { initialEdges, initialNodes } from './initial-elements.js'
import { useRunProcess } from '@/views/dataflow-chat/useRunProcess.js'
import { useShuffle } from '@/views/dataflow-chat/useShuffle.js'
import { useLayout } from '@/views/dataflow-chat/useLayout.js'

import moment from "moment-mini";
import {reactive, ref} from 'vue'

interface DatabaseConfig {
  host: string,
  user: string,
  password: string,
  database: string,
  port: string,
  ddl: []
}

interface DataflowMessage {
  role: string;
  ask: string;
  content: string;
  time: string;
  loading: boolean;
  query: string;
  queryResult: object;
  queryChatOption: object;
}

const DATAFLOW_CHAT_HISTORY_KEY = 'dbgpt-data-flow-history'

const DATAFLOW_OPTIONS_KEY = 'dbgpt-dataflow-options'

const DATAFLOW_PROMPT_KEY = 'dbgpt-dataflow-prompt'

const llmModel: Ref<string> = ref('')

const modelList = ref<string[]>([])

const historyLength: Ref<number> = ref(3)

const databaseOptionList = ref<object[]>([])

const databaseSelect = reactive<DatabaseConfig>({
  host: '',
  user: '',
  password: '',
  database: '',
  port: '',
  ddl: []
})

const ruleFormRef = ref<FormInstance>()

const promptFormRef = ref<FormInstance>()

const dialogEditDatabaseVisible = ref(false)

const dialogPromptConfigVisible = ref(false)

const isEditDatabaseForm = ref(false)

const editDatabaseForm = reactive({
  host: '',
  user: '',
  password: '',
  database: '',
  port: '',
  ddl: [],
  intor: '',
  prompt: ''
})

const promptConfigForm = reactive({
  visulization_prompt: '你是一个数据科学可视化专家, 任务是选择最好的可视化方法来展示数据.\n' +
      '用户输入的自然语言查询为: {query}.\n' +
      '自动产生的 SQL 语句为: {sql}.\n' +
      '数据库的模式(schema)为: {schema}.\n' +
      '你可以选择的可视化方法有: \n' +
      '(1)折线图 (2)柱状图 (3)饼状图 (4) 散点图\n' +
      '并有以下额外要求: \n' +
      '(1) 只能从 SQL 语句的结果中选择可视化的对象\n' +
      '现在你只需要在下面的选择中选择最好的方法并回答三点: 方法名称, 和图像设计, 设计理由(理由应详细且合理)\n' +
      '回答必须类似于以下可以被反序列化的 json 格式, 其中所有轴的命名应该与 SQL 的列名匹配:\n' +
      '{{"method": "折线图", "design": {{"xAxis": "weekday", "yAxis": "number"}}, "reason": "该图像以时间为自变量, 数量为因变量体现变化趋势."}}\n' +
      '{{"method": "柱状图", "design": {{"xAxis": "category", "yAxis": "value"}}, "reason": "该图像通过将各种种类的价值不同柱体现差异."}}\n' +
      '{{"method": "饼状图", "design": {{"value": "percentage", "pie_name": "type"}}, "reason": "该图像显示各个类型所占百分比, 以体现各自份额."}}\n' +
      '{{"method": "散点图", "design": {{"xAxis": "time", "yAxis": "height"}}, "reason": "该图像显示时间和高度的散点关系."}}',
  query_prompt: '额外要求如下: (1) 对于聚合函数, 请为相应的列命名 (2) 如果可能的话, 请做排序 (3) SQL 语句应尽量精简'
})

const messageList: Ref<DataflowMessage[]> = ref([]);

const messagesScrollDiv = ref<HTMLElement | null>(null);

const ddlActiveName = ref('0')

const nodes = ref(initialNodes)

const edges = ref(initialEdges)

const cancelOnError = ref(true)

const shuffle = useShuffle()

const { graph, layout, previousDirection } = useLayout()

const { run, stop, reset, isRunning } = useRunProcess({ graph, cancelOnError })

const { fitView } = useVueFlow()

const currentNodeMessage = reactive<DataflowMessage>({
  role: '',
  ask: '',
  content: '',
  time: '',
  loading: false,
  query: '',
  queryResult: {},
  queryChatOption: {}
})

watch(() => messageList.value, () => {
  nextTick(() => {
    if (messagesScrollDiv.value) {
      messagesScrollDiv.value.scrollTop = messagesScrollDiv.value.scrollHeight;
    }
  })
})

onMounted(() => {
  nextTick(() => {
    databaseOptionList.value = JSON.parse(localStorage.getItem(DATAFLOW_OPTIONS_KEY) || '[]')
    // if (databaseOptionList.value.length === 0) {
    //   databaseOptionList.value.push({
    //     host: '127.0.0.1',
    //     user: 'root',
    //     password: '123456',
    //     database: 'test',
    //     port: '3306',
    //     ddl: []
    //   })
    // }
    if (databaseOptionList.value.length > 0) {
      onDatabaseClick(databaseOptionList.value[0])
    }
    const promptConfig = JSON.parse(localStorage.getItem(DATAFLOW_PROMPT_KEY) || '{}')
    if (promptConfig.visulization_prompt) {
      promptConfigForm.visulization_prompt = promptConfig.visulization_prompt
    }
    if (promptConfig.query_prompt) {
      promptConfigForm.query_prompt = promptConfig.query_prompt
    }
    getLlmModelListModels()
    messageList.value = getLocalHistoryMessages()
    Object.assign(currentNodeMessage, getLastMessage())
  })
});

const onDatabaseClick = (item) => {
  if(JSON.stringify(item) === JSON.stringify(databaseSelect)) {
    return
  }
  Object.assign(databaseSelect, item)
  messageList.value = getLocalHistoryMessages()
}

const resetDatabaseForm = (item) => {
  editDatabaseForm.host = item?.host || "";
  editDatabaseForm.user = item?.user || "";
  editDatabaseForm.password = item?.password || "";
  editDatabaseForm.database = item?.database || "";
  editDatabaseForm.port = item?.port || "";
  editDatabaseForm.ddl = item?.ddl || [];
}

const onAddDatabaseOptionClick = () => {
  resetDatabaseForm({})
  isEditDatabaseForm.value = false
  ddlActiveName.value = '0'
  dialogEditDatabaseVisible.value = true
}

const onEditDatabaseOptionClick = (item) => {
  resetDatabaseForm(item)
  isEditDatabaseForm.value = true
  ddlActiveName.value = '0'
  dialogEditDatabaseVisible.value = true
}

const onDatabaseDDLClick = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      dbDdlInfoReq(editDatabaseForm).then(res => {
        editDatabaseForm.ddl = res.data
      })
    }
  })
}

const saveDatabaseOptionsToLocalStorage = () => {
  localStorage.setItem(DATAFLOW_OPTIONS_KEY, JSON.stringify(databaseOptionList.value))
}

const saveDatabasePromptToLocalStorage = () => {
  localStorage.setItem(DATAFLOW_PROMPT_KEY, JSON.stringify(promptConfigForm))
}

const onDeleteDatabaseOptionClick = (item) => {

  ElMessageBox.confirm(
      'Will delete the Database. Continue?',
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
  )
      .then(() => {
        databaseOptionList.value = databaseOptionList.value.filter(i => i['host'] + i['database'] !== item.host + item.database)
        saveDatabaseOptionsToLocalStorage()
        if (databaseOptionList.value.length > 0) {
          onDatabaseClick(databaseOptionList.value[0])
        }else {
          onDatabaseClick({})
        }
      }).catch(() => {})
}

const onCreateDatabaseClick = () => {
  ruleFormRef.value.validate((valid) => {
    if (!valid) return;

    const index = databaseOptionList.value.findIndex(i => i['host']+i['database'] === editDatabaseForm.host+editDatabaseForm.database)
    if (index >= 0 && !isEditDatabaseForm.value) {
      ElMessage.error('Database already exists')
      return;
    }
    if (index >= 0) {
      databaseOptionList.value[index] = editDatabaseForm
    } else {
      databaseOptionList.value.push(editDatabaseForm)
    }
    Object.assign(databaseSelect, databaseOptionList.value[0])
    saveDatabaseOptionsToLocalStorage()
    dialogEditDatabaseVisible.value = false
  })
}

const onPromptConfigClick = () => {
  dialogPromptConfigVisible.value = true
}

const onSavePromptClick = () => {
  promptFormRef.value.validate((valid) => {
    if (valid) {
      saveDatabasePromptToLocalStorage()
      dialogPromptConfigVisible.value = false
    }
  })
}

const getLlmModelListModels = async () => {
  llmModelListModelsReq().then(res => {
    modelList.value = res.data || [];
    llmModel.value = modelList.value[0]
  })
}

const addUserMessage = (content: string) => {
  const userMessage: DataflowMessage = {
    role: 'user',
    ask: '',
    content,
    time: moment().format('YYYY-MM-DD HH:mm:ss'),
    loading: false,
    query: '',
    queryResult: {},
    queryChatOption: {}
  }
  messageList.value.push(userMessage)
}

const addRobotMessage = (content: string, ask: string) => {
  const robotMessage: DataflowMessage = {
    role: 'assistant',
    ask,
    content,
    time: moment().format('YYYY-MM-DD HH:mm:ss'),
    loading: true,
    query: '',
    queryResult: {},
    queryChatOption: {}
  }
  messageList.value.push(robotMessage)
}

const updateLastRobotMessage = (query='', queryResult={}, queryChatOption={}, loading = false) => {
  const lastMessageIndex = messageList.value.length - 1;
  const lastMessage = messageList.value[lastMessageIndex];
  const updatedMessage = {
    ...lastMessage,
    loading,
    query: query ? query : lastMessage.query,
    queryResult: Object.keys(queryResult).length > 0 ? queryResult : lastMessage.queryResult,
    queryChatOption: Object.keys(queryChatOption).length > 0 ? queryChatOption : lastMessage.queryChatOption
  };
  messageList.value[lastMessageIndex] = updatedMessage;
};

const updateLastRobotMessageLoading = (loading: boolean) => {
  const lastMessageIndex = messageList.value.length - 1;
  const lastMessage = messageList.value[lastMessageIndex];
  const updatedMessage = {
    ...lastMessage,
    loading,
  };
  messageList.value[lastMessageIndex] = updatedMessage;
  lastMessage.loading = loading
}

const getHistoryMessages = () => {
  return messageList.value.slice(-historyLength.value).map(item => {
    return {
      role: item.role,
      content: item.content
    }
  })
}

const saveHistoryMessagesToLocal = () => {
  localStorage.setItem(`${DATAFLOW_CHAT_HISTORY_KEY}-${databaseSelect.host}-${databaseSelect.database}`, JSON.stringify(messageList.value))
}

const getLocalHistoryMessages = () => {
  const historyMessages = JSON.parse(localStorage.getItem(`${DATAFLOW_CHAT_HISTORY_KEY}-${databaseSelect.host}-${databaseSelect.database}`) || '[]')
  return historyMessages.map((item: DataflowMessage) => {
    return {
      role: item.role,
      ask: item.ask,
      content: item.content,
      time: item.time,
      loading: item.loading,
      query: item.query,
      queryResult: item.queryResult || {},
      queryChatOption: item.queryChatOption || {}
    };
  });
}

const getLastMessage = () => {
  const lastMessageIndex = messageList.value.length - 1;
  return messageList.value[lastMessageIndex];
}

const onSendClick = (value) => {
  if (!databaseSelect.host) {
    ElMessage.error('Please select database')
    return
  }
  if (value === '') {
    ElMessage.error('Please input something')
    return
  }

  const userInputValue = value

  addUserMessage(userInputValue)
  saveHistoryMessagesToLocal()
  addRobotMessage('', userInputValue)
  saveHistoryMessagesToLocal()
  dbGenerateSqlReq(`${userInputValue}\n${promptConfigForm.query_prompt}`, JSON.stringify(databaseSelect['ddl'] || []), llmModel.value).then(res => {
    updateLastRobotMessage(res.answer, [], [], true)
    saveHistoryMessagesToLocal()
    dbExecuteSql(res.answer)
  }).catch((error) => {
    updateLastRobotMessageLoading(false)
    saveHistoryMessagesToLocal()
  })
}

const dbExecuteSql = (query)  => {
  dbExecuteSqlReq(query, databaseSelect['host'], databaseSelect['user'], databaseSelect['password'], databaseSelect['database'],
      Number.parseInt(databaseSelect['port'])).then(res => {
    updateLastRobotMessage('', res.data, {}, true)
    saveHistoryMessagesToLocal()
    chat()
  }).catch(() => {
    updateLastRobotMessageLoading(false)
  })
}

const chat = ()  => {
  const lastMessage = getLastMessage()
  const prompt = promptConfigForm.visulization_prompt.replace('{query}', lastMessage.ask).replace('{sql}', lastMessage.query).replace('{schema}', JSON.stringify(databaseSelect['ddl'] || []))
  chatReq(prompt, "", llmModel.value, [], 0).then(res => {
    updateLastRobotMessage('', {}, JSON.parse(res.text), false)
    saveHistoryMessagesToLocal()
  }).catch(() => {
    updateLastRobotMessageLoading(false)
  })
}

async function layoutGraph(direction) {
  nodes.value = layout(nodes.value, edges.value, direction)
  console.log('========:', nodes.value)
  nextTick(() => {
    // fitView()
  })
}

</script>

<style>
.database-select .el-select__wrapper {
  background-color: var(--el-color-primary-light-9);
  border-radius: 8px
}
</style>

<style>
.layout-flow {
  position: relative;
  background-color: #1a192b;
  height: 300px;
  width: 100%;
  border-radius: 8px;
}

.process-panel {
  background-color: #2d3748;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 10px;
}

.add-container {
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  color: var(--el-color-primary);
  border: 1px solid var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.add-container:hover {
  background: var(--el-color-primary);
  color: white;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

<style lang="scss" scoped>
.chat-container {
  height: calc(100vh - 40px);
  overflow: hidden;

  .sidebar {
    width: 180px;
    border-right: 1px solid #eeeeee;
    display: flex;
    height: 100vh;
    padding: 10px 20px;
  }

  .messages-container {
    height: calc(100vh - 440px);
    width: 100%;
    flex-shrink: 1;
    background: transparent;
    overflow-y: auto;
    padding-bottom: 20px;
  }

  .database-select-item {
    width: 100%;
    margin-bottom: 10px;
    padding: 10px 10px;
    border-radius: 10px;
    cursor: pointer;
    border: 1px solid var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    .el-text {
      color: var(--el-color-primary)!important;
    }
    .el-icon {
      margin-right: 10px;
    }

    &:hover {
      background: var(--el-color-primary);
      .el-text {
        color: white!important;;
      }
    }

    &.active {
      background: var(--el-color-primary);
      .el-text {
        color: white!important;;
      }
    }
  }
}
</style>
