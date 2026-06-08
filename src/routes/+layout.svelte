<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav>
	<a href="/Energy-Hub/">home</a>
	<a href="/Energy-Hub/about">about</a>
</nav>

{@render children()}
