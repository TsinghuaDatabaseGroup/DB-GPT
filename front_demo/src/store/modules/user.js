// import { login } from '@/api/user'
import { getToken, getUserId, removeToken, removeUserId, setToken, setUserId } from '@/utils/auth'
import { resetRouter } from '@/router'
// import md5 from 'js-md5'

const getDefaultState = () => {
  return {
    token: getToken(),
    name: '',
    userId: getUserId(),
    avatar: ''
  }
}

const state = getDefaultState()

const mutations = {
  RESET_STATE: (state) => {
    Object.assign(state, getDefaultState())
  },
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    console.log('avatar:', avatar)
    state.avatar = avatar
  },
  SET_USERID: (state, name) => {
    state.userId = name
  }
}

const actions = {
  // user login
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      console.log(username, password)
      const data = {
        user_id: '12312312312312',
        access_token: 'access_tokenaccess_tokenaccess_tokenaccess_token'
      }
      commit('SET_USERID', data.user_id)
      commit('SET_TOKEN', data.access_token)
      setToken(data.access_token)
      setUserId(data.user_id)
      resolve()
      // login({ username: username.trim(), password: md5(password) }).then(response => {
      //   const { data } = response
      //   commit('SET_USERID', data.user_id)
      //   commit('SET_TOKEN', data.access_token)
      //   setToken(data.access_token)
      //   setUserId(data.user_id)
      //   resolve()
      // }).catch(error => {
      //   reject(error)
      // })
    })
  },

  // get user info
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      const data = {
        username: 'DBGPT',
        avatar: ''
      }

      const { username, avatar } = data

      commit('SET_NAME', username)
      commit('SET_AVATAR', avatar)

      resolve(data)

      // userInfo(state.token).then(response => {
      //   const { data } = response
      //
      //   if (!data) {
      //     return reject('Verification failed, please Login again.')
      //   }
      //
      //   const { username, avatar } = data
      //
      //   commit('SET_NAME', username)
      //   commit('SET_AVATAR', avatar)
      //
      //   resolve(data)
      // }).catch(error => {
      //   reject(error)
      // })
    })
  },

  // user logout
  logout({ commit, state }) {
    removeToken()
    removeUserId()
    resetRouter()
    commit('RESET_STATE')
    // return new Promise((resolve, reject) => {
    //   logout(state.token).then(() => {
    //     removeToken() // must remove  token  first
    //     resetRouter()
    //     commit('RESET_STATE')
    //     resolve()
    //   }).catch(error => {
    //     reject(error)
    //   })
    // })
  },

  // remove token
  resetToken({ commit }) {
    return new Promise(resolve => {
      removeToken() // must remove  token  first
      removeUserId()
      commit('RESET_STATE')
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

