<script>
	import '../app.css';
	import ProfileDropdown from '$lib/components/ProfileDropdown.svelte';
	import { page } from '$app/state';

	let { data, children } = $props();

	import { shouldHideProfile } from '$lib/config/layout.js';

	let hideProfileDropdown = $derived(shouldHideProfile(page.route.id));
</script>

<main>

	{#if !hideProfileDropdown}
		{#if data.session?.user}
			<div class="profile-nav">
				<ProfileDropdown user={data.session.user} />
			</div>
		{/if}
	{/if}
	
	{@render children()}
</main>

<style>
	.profile-nav {
		position: fixed;
		top: 0.5rem;
		right: 0.5rem;
		z-index: 100;
	}
	
	main {
		min-height: 100vh;
	}
</style>
