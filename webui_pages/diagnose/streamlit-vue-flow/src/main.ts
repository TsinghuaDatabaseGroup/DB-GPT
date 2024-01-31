import Vue from 'vue'
import App from './App.vue'
import { Popover } from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css';

Vue.component(Popover.name, Popover);
Vue.config.productionTip = false
Vue.prototype.$ELEMENT = { size: 'small', zIndex: 3000 };

new Vue({
  render: h => h(App),
}).$mount('#app')
