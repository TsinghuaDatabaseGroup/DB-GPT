import axiosReq from 'axios'
// export const userInfoReq = (): Promise<any> => {
//   return new Promise((resolve) => {
//     const reqConfig = {
//       url: '/basis-func/user/getUserInfo',
//       params: { plateFormId: 2 },
//       method: 'post'
//     }
//     axiosReq(reqConfig).then(({ data }) => {
//       resolve(data)
//     })
//   })
// }

//登录
export const loginReq = (subForm) => {
  return axiosReq({
    url: '/mock/login',
    params: subForm,
    method: 'post'
  })
}

//退出登录
export const loginOutReq = () => {
  return axiosReq({
    url: '/mock/loginOut',
    method: 'post'
  })
}
