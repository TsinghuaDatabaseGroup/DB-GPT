import Cookies from 'js-cookie'

const TokenKey = 'dbgpt_admin_token'
const UserIdKey = 'dbgpt_admin_userid'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

export function getUserId() {
  return Cookies.get(UserIdKey)
}

export function setUserId(token) {
  return Cookies.set(UserIdKey, token)
}

export function removeUserId() {
  return Cookies.remove(UserIdKey)
}
