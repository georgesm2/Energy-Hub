<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { resolve } from '$app/paths';
	import '../styles.css';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav class="navbar">
	<h1>UK Energy Dashboard</h1>
	<a href={resolve('/')}>home</a>
	<a href={resolve('/about')}>about</a>
</nav>

{@render children()}
