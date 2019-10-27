<template>
  	<div class="smart-water">
		<ui-toolbar brand="SmartWMS" title="Sensor Map" type="colored" textColor="white">
			<img slot="icon" src="../../public/logo_drop.png" class="icon" />
			<ui-button
				slot="actions"
				color="primary"
				type="primary"
				@click="openRegisterModal">
				Register New Sensor
			</ui-button>
		</ui-toolbar>

		<div class="smart-water-body">

			<div class="smart-water-body-map">
				<div class="flex">
					<multiselect class="search-field" v-model="model" :options="options" placeholder="Search for Sensor..." label="name" track-by="name" @search-change="searchChange" ></multiselect>
					
					<!-- <ui-textbox class="smart-water-search" v-model="searchString" placeholder="Search for Sensors..." @key-enter="searchSensors" /> -->
					<ui-button color="primary" :disabled="!searchString" @click="searchSensors">Search</ui-button>
				</div>

				<div class="smart-water-body-map">
					<l-map :zoom="map.zoom" :center="map.center">
						<l-tile-layer :url="map.url" :attribution="map.attribution"></l-tile-layer>
						<l-marker v-for="marker in markers" :key="marker.id" :icon="map.icon" :lat-lng="marker.pos" title="marker.name" @click="openChartModal(marker)" />
					</l-map>
				</div>
			</div>


			<ui-modal class="smart-wms-body-modal" ref="chart" :title="`Sensor ${dataSource.marker.name} at ${dataSource.marker.locationName}`" size="auto">
				<fusioncharts
					class="smart-wms-body-modal-chart"
					:type="type"
					width="800"
					height="500"
					:dataFormat="dataFormat"
					:dataSource="dataSource">
				</fusioncharts>
			</ui-modal>

			<ui-modal class="smart-wms-body-modal" ref="register" title="Add new Sensor">
				<ui-textbox type="text" v-model="sensor.name" label="Name" />
				<ui-textbox type="text" v-model="sensor.locationName" label="Location Name" />
				<ui-textbox type="number" v-model="sensor.id" label="Sensor ID" />

				<ui-checkbox v-model="sensor.hasGPS" label="Sensor has GPS"/>
				<ui-textbox type="number" v-model="sensor.lat" label="Lat" :disabled="sensor.hasGPS" />
				<ui-textbox type="number" v-model="sensor.long" label="Lng" :disabled="sensor.hasGPS" />
				<div class="flex">
					<ui-button @click="saveSensor" color="green" :disabled="isSaveButtonDisabled" :loading="sensor.loading">Save Sensor</ui-button>
					<ui-button @click="openMap" color="primary" :disabled="sensor.hasGPS">Pick Position</ui-button>
				</div>
			</ui-modal>

			<ui-modal class="smart-wms-body-modal-geopicker" ref="geoPicker" title="Pick your Location" size="auto">
				<geo-picker :search="sensor.locationName" @update="updateGeoLocation"/>
			</ui-modal>
		</div>
  	</div>
</template>

<script>

import GeoPicker from './GeoPicker'
import { UiTextbox, UiButton, UiSelect, UiIconButton, UiIcon, UiToolbar, UiModal, UiCheckbox } from 'keen-ui'

import Multiselect from 'vue-multiselect'

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
		GeoPicker,
		UiTextbox,
		UiButton,
		UiCheckbox,
		UiIconButton,
		UiToolbar,
		UiModal,
		FusionCharts,
		VueFusionCharts,
		LMap,
		LTileLayer,
		LMarker,
		Vue2LeafletLocatecontrol,
		Multiselect
	},

	computed: {
		isSaveButtonDisabled(){
			return !this.sensor.name || !this.sensor.locationName || !this.sensor.id || (!this.sensor.hasGPS && (!this.sensor.lat || !this.sensor.long))
		}
	},

	data() {
		return {
			model: {id: '-1', name: 'Search...'},
			options: [],
			sensor: {
				loading: false,
				hasGPS: false,
				name: '',
				locationName: '',
				id: '',
				lat: '',
				long: ''
			},
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
		async searchChange(value){
			this.$http.get(host + `sensors?name=${value}`)
				.then((response) => {
					if(response.body.length === 0){
						return
					}
					this.options = []
					response.body.forEach(e => {
						this.options.push({value: e.id, name: e.name})
					});
				});
		},
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
			this.$http.get(host + 'sensors')
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
		openChartModal(marker){
			this.getSensorHistory(marker.id)
			this.dataSource.caption = `Sensor ${marker.name}`
			this.dataSource.marker.id = marker.id
			this.dataSource.marker.name = marker.name
			this.dataSource.marker.locationName = marker.locationName
			this.$refs['chart'].open();
		},
		openRegisterModal(){
			this.$refs['register'].open();
		},
		saveSensor(){
			this.sensor.loading = true
			let lat = this.sensor.lat
			let lng = this.sensor.long
			if(this.sensor.hasGPS){
				lat = 48.4797217
				lng = 7.9212435
			}
			this.$http.post(host + 'sensor/create', {
					latitude: lat,
					longitude: lng,
					name: this.sensor.name,
					loc_name: this.sensor.locationName,
					dev_uid: this.sensor.id
				})
				.then((response) => {
					this.sensor.loading = false
					this.$refs['register'].close();
					this.getSensors()
				})
		},
		openMap(){
			this.$refs['geoPicker'].open();
		},
		updateGeoLocation(location){
			this.sensor.lat = location.lat
			this.sensor.long = location.lng
			this.$refs['geoPicker'].close();	
		}
	}
}

</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style scoped>

.multiselect__content-wrapper > *{
	z-index: 11000;
}

.search-field {
	margin-right: 2em;
	vertical-align: middle;
	z-index: 1100;
}

.icon {
	height: 2em;
	width: auto;
	border-radius: 50%;
	margin-left: 1em;
	vertical-align: middle;
}

.leaflet-top{
	z-index: 901;
}

.flex{
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 1em;
}

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
.smart-water-search {
	width: 70%;	
	margin-right: 1em;
}

.smart-wms-body-modal {
	z-index: 1200;
	text-align: center;
}

.smart-wms-body-modal-chart{
	display: inline-block;
	width: 800px;
	height: 500px;
}

.smart-wms-body-modal-geopicker {
	z-index: 1300;
}


</style>