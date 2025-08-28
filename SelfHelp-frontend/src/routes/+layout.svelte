<script>
	import '../app.css';
	import ProfileDropdown from '$lib/components/ProfileDropdown.svelte';
	
	let { data, children } = $props();
</script>

<main>
	{#if data.session?.user}
		<div class="profile-nav">
			<ProfileDropdown user={data.session.user} />
		</div>
	{/if}
	
	{@render children()}
</main>

<style>
	.profile-nav {
		position: fixed;
		top: 1rem;
		right: 1rem;
		z-index: 100;
	}
	
	main {
		min-height: 100vh;
	}
</style>
