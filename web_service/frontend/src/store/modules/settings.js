import defaultSettings from '@/settings'

const { showSettings, fixedHeader, sidebarLogo } = defaultSettings

const state = {
  showSettings: showSettings,
  fixedHeader: fixedHeader,
  sidebarLogo: sidebarLogo,
  model: sessionStorage.getItem('UseModel') || 'GPT4-0613'
}

const mutations = {
  CHANGE_SETTING: (state, { key, value }) => {
    // eslint-disable-next-line no-prototype-builtins
    if (state.hasOwnProperty(key)) {
      state[key] = value
    }
  },
  SET_MODEL: (state, model) => {
    state.model = model
  }
}

const actions = {
  changeSetting({ commit }, data) {
    commit('CHANGE_SETTING', data)
  },
  model({ commit }, data) {
    sessionStorage.setItem('UseModel', data)
    commit('SET_MODEL', data)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

