<script lang="ts">
	
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children?.()}


<style>
	main {
		display: flex;
		flex-direction: column;
		/*padding: 1rem;*/
		width: 100%;
		max-width: 100%;
		margin: 0 auto;
		box-sizing: border-box;
		min-height: 100vh;
	}
</style>