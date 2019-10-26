<template>
	<div id="app">
		<smart-water />
	</div>
</template>

<script>

import SmartWater from './components/SmartWater'
import 'keen-ui/dist/keen-ui.css'

export default {

	name: 'app',

	components: {
		SmartWater
	}
}
</script>

<style>

*,
*::before,
*::after {
    box-sizing: border-box;
}

html {
	font-size: 100%;
}
body {
	margin: 0;
}

#app {
	font-family: 'Avenir', Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}

</style>
