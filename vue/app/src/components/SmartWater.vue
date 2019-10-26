<template>
  	<div class="smart-water">
		<ui-toolbar navIcon="menu" brand="SmartWMS" title="Sensor Map" type="colored" textColor="white" :raised="false" :removeNavIcon="true">
			<div slot="actions">
				<ui-icon-button
					color="black"
					size="large"
					type="secondary">
					<add-icon slot="icon" />
				</ui-icon-button>
			</div>
		</ui-toolbar>

		<div class="smart-water-body">
			<div class="smart-water-search">
				<ui-textbox type="text" v-model="searchString" :invalid="!!searchError" :error="searchError" placeholder="Adresse, Name, Ort, ..." @keydown-enter="searchSensors" />
				<ui-button @click="searchSensors">suche</ui-button>
			</div>

			<ui-modal class="smart-wms-body-modal" ref="chart" :title="`Sensor ${dataSource.marker.name} bei ${dataSource.marker.locationName}`" size="auto">
				<fusioncharts
					class="smart-wms-body-modal-chart"
					:type="type"
					width="800"
					height="500"
					:dataFormat="dataFormat"
					:dataSource="dataSource">
				</fusioncharts>

			</ui-modal>

			<div class="smart-water-body-map">
				<l-map :zoom="map.zoom" :center="map.center">
					<l-tile-layer :url="map.url" :attribution="map.attribution"></l-tile-layer>
					<l-marker v-for="marker in markers" :key="marker.id" :icon="map.icon" :lat-lng="marker.pos" @click="openModal(marker)"></l-marker>
				</l-map>
			</div>
		</div>
  	</div>
</template>

<script>

import Vue from 'vue'
import { UiTextbox, UiButton, UiIconButton, UiToolbar, UiModal } from 'keen-ui'

import AddIcon from 'vue-material-design-icons/Add'

import VueFusionCharts from 'vue-fusioncharts'
import FusionCharts from 'fusioncharts'
import Charts from 'fusioncharts/fusioncharts.charts'

import { OpenStreetMapProvider } from 'leaflet-geosearch'
import Vue2LeafletLocatecontrol from 'vue2-leaflet-locatecontrol'
import {LMap, LTileLayer, LMarker} from 'vue2-leaflet'
import Lf from 'leaflet'
import { Icon } from 'leaflet'
import 'leaflet/dist/leaflet.css'

const host = 'http://10.16.1.1:6969/'
const distance = 10000

export default {

	name: 'smart-water',

	components: {
		UiTextbox,
		UiButton,
		UiIconButton,
		UiToolbar,
		UiModal,
		AddIcon,
		FusionCharts,
		VueFusionCharts,
		LMap,
		LTileLayer,
		LMarker,
		Vue2LeafletLocatecontrol
	},

	data() {
		return {
			markers: [],
			dataSource: {
				marker: {
					id: 13456,
					name: 'default',
					locationName: 'default'
				},
				chart: {
					caption: "",
					subCaption: "",
					showValues:"0",
					showPercentInTooltip: "1",
					enableMultiSlicing:"0",
					theme: "fusion"
				},
				data: []
			},
			type: 'line',
			dataFormat: 'json',

			provider: new OpenStreetMapProvider(),
			searchString: '',
			searchError: '',
			map: {
				zoom: 3,
				center: Lf.latLng(47.413220, -1.219482),
				url:'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
				attribution:'&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
				icon: L.icon({
					iconUrl: require('../assets/marker.png'),
					iconSize: [30, 30],
					iconAnchor: [15, 30]
				})
			}
		}
	},

	mounted(){
		this.getSensors()
	},
	
	methods: {
		async searchSensorsByPos(lat, long){
			this.$http.get(host + `sensors?lat=${lat}&long=${long}&dist=${this.distance}`)
				.then((response) => {
					if(response.body.length === 0){
						
						this.searchError = 'Keine Sensoren gefunden'
						return
					}
					this.markers = []
					response.body.forEach(e => {
						this.markers.push({id: e.id, name: e.name, pos: Lf.latLng(e.lat, e.long), lastMessure: e.last_measurement, locationName: e.loc_name})
					});
					this.map.center = this.markers[0].pos
					this.map.zoom = 10
					this.searchError = ''
				});
		},
		async searchSensors(){
			this.$http.get(host + `sensors?name=${this.searchString}`)
				.then((response) => {
					if(response.body.length === 0){
						this.provider.sea
						this.searchSensorsByPos(lat, long)
						return
					}
					this.markers = []
					response.body.forEach(e => {
						this.markers.push({id: e.id, name: e.name, pos: Lf.latLng(e.lat, e.long), lastMessure: e.last_measurement, locationName: e.loc_name})
					});
					this.map.center = this.markers[0].pos
					this.map.zoom = 10
					this.searchError = ''
				});
		},
		async getSensors(){
			this.$http.get(host + 'sensors')//dwarvenforge.de
				.then((response) => {
					this.markers = []
					response.body.forEach(e => {
						this.markers.push({id: e.id, name: e.name, pos: Lf.latLng(e.lat, e.long), lastMessure: e.last_measurement, locationName: e.loc_name})
					});
				});
		},
		async getSensorHistory(id){
			this.$http.get(host + `sensor/history?id=${id}`)
				.then((response) => {
					let data = []
					response.body.forEach(e => {
						data.push({label: e.time, value: e.height})
					})
					this.dataSource.data = data
				});
		},
		openModal(marker){
			this.getSensorHistory(marker.id)
			this.dataSource.caption = `Sensor ${marker.name}`
			this.dataSource.marker.id = marker.id
			this.dataSource.marker.name = marker.name
			this.dataSource.marker.locationName = marker.locationName
			this.$refs['chart'].open();
		}
	}
}

</script>

<style scoped>

.smart-water-body {
	padding: 1em;
	text-align: center;
}

.smart-water-body-map {
	display: inline-block;
	width: 950px;
	height: 550px;
}

.smart-water-search{
	width: 100%;
	display: flex;
	align-items: center;
	justify-content: space-between;
}
.smart-water-search .ui-textbox{
	width: 70%;	
	margin-right: 1em;
}


.smart-wms-body-modal {
	z-index: 900;
	text-align: center;
}

.smart-wms-body-modal-chart{
	display: inline-block;
	width: 800px;
	height: 500px;
}
</style>