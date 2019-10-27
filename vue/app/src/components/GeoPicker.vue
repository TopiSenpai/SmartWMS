<template>
    <div class="geo-picker">
        <div class="geo-picker-search">
            <multiselect class="search-field" v-model="model" :options="options" placeholder="Search for Sensor..." label="name" track-by="name" @select="selectGeoLocation" @search-change="searchGeoLocation"></multiselect>
            <ui-button @click="searchGeoLocation" color="primary" :disabled="!searchString">Search</ui-button>
        </div>

        <div class="geo-picker-map">
            <l-map :zoom="zoom" :center="center">
                <l-tile-layer :url="url" :attribution="attribution"></l-tile-layer>
                <l-marker :icon="icon" :lat-lng="marker" :draggable="true" @drag="updateGeoLocation"></l-marker>
            </l-map>
        </div>
        <ui-button color="green" @click="saveGeoLocation">Save Geo Location</ui-button>
    </div>
</template>

<script>

import Multiselect from 'vue-multiselect'
import { UiButton, UiTextbox } from 'keen-ui'
import { OpenStreetMapProvider } from 'leaflet-geosearch'
import Vue2LeafletLocatecontrol from 'vue2-leaflet-locatecontrol'
import {LMap, LTileLayer, LMarker} from 'vue2-leaflet'
import Lf from 'leaflet'
import { Icon } from 'leaflet'
import 'leaflet/dist/leaflet.css'

export default {

    name: 'geo-picker',
    
    props: {
        search: {
            require: false,
            type: String,
            defauilt: ''
        }
    },

	components: {
		UiTextbox,
		UiButton,
		LMap,
		LTileLayer,
		LMarker,
        Vue2LeafletLocatecontrol,
        Multiselect
    },

    data(){
        return {
            model: {id: '-1', name: 'Search...'},
			options: [],
            provider: new OpenStreetMapProvider(),
			searchString: this.search,
			searchError: '',
            marker: Lf.latLng(47.413220, -1.219482),
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
    },
    
    methods: {
        searchGeoLocation(value){
			this.provider
                .search({ query: value })
                .then((response) => { 
					if(response.length === 0){
                        this.searchError = 'Keine Sensoren gefunden'
						return
					}
                    this.options = []
                    console.log(response)
					response.forEach(e => {
						this.options.push({value: Lf.latLng(e.y, e.x), name: e.label})
                    });
				});
		},
        selectGeoLocation(place){
            console.log('PICK GEO LOCATION', place, place.value)     
            this.marker = place.value
            this.center = this.marker
            this.zoom = 10
            this.searchError = ''
        },
        updateGeoLocation(marker){
            this.marker = marker.latLng
        },
        saveGeoLocation(){
			this.$emit('update', this.marker)
		},
    }
}
</script>

<style scoped>

.multiselect__content-wrapper > *{
	z-index: 11000;
}

.search-field {
	margin-right: 2em;
	vertical-align: middle;
	z-index: 1100;
}

.geo-picker-map{
    width: 500px;
    height: 400px;
    margin-bottom: 1em;
}

.geo-picker-search{
    display: flex;
	align-items: center;
	justify-content: space-between;

}

.geo-picker-search .ui-textbox{
	width: 70%;	
	margin-right: 1em;
}

</style>