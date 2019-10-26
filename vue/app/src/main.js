import Vue from 'vue'
import App from './App.vue'
import VueResource from 'vue-resource'

import VueFusionCharts from 'vue-fusioncharts';
import FusionCharts from 'fusioncharts';
import Charts from 'fusioncharts/fusioncharts.charts'
import 'vue-material-design-icons/styles.css';

Vue.use(VueFusionCharts, FusionCharts, Charts)


Vue.use(VueResource);
Vue.config.productionTip = false

new Vue({
	render: h => h(App),
}).$mount('#app')
