import { post } from '@/api/request'

export async function login(args) {
  console.log('login:', args)
  return await post('admin/login', args)
}

export async function userInfo() {
  return await post('admin/user/info', {})
}

// export async function logout(args) {
//   console.log('login:', args)
//   return await post('admin/user/info', args)
// }

// export function logout() {
//   return request({
//     url: '/vue-admin-template/user/logout',
//     method: 'post'
//   })
// }
