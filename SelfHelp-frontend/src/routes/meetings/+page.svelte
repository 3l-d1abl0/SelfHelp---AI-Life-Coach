<script lang="ts">
	import type { PageData } from './$types';
	
	let { data }: { data: PageData } = $props();
	const { user } = data;
</script>

<svelte:head>
	<title>My Meetings</title>
</svelte:head>

<div class="page-container">
    My Meetings
</div>