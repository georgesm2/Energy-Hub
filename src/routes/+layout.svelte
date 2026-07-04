<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { resolve } from '$app/paths';
	import '../styles.css';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>UK Energy Dashboard</title>
	<meta name="description" content="UK Energy Dashboard" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
</svelte:head>

<nav class="navbar">
	<h1>UK Energy Dashboard</h1>
	<div class="nav-links">
		<a href={resolve('/')}>home</a>
		<a href={resolve('/about')}>about</a>
	</div>
</nav>

{@render children()}
