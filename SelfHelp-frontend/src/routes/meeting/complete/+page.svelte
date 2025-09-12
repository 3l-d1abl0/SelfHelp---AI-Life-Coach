<script lang="ts">

	import type { PageData } from './$types';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

    let { data }: { data: PageData } = $props();
	const { user } = data;
	console.log('USER: ', user);
	
	let showNewMeetingButton: boolean = $state(false);
	
	onMount(() => {
		// Show the new meeting button after 3 seconds
		setTimeout(() => {
			showNewMeetingButton = true;
		}, 3000);
	});
	
	function startNewMeeting() {
		goto('/meeting/new');
	}
</script>

<svelte:head>
	<title>Meeting Complete</title>
</svelte:head>

<div class="complete-screen">
	<div class="complete-content">
		<div class="complete-icon">
			<svg width="100" height="100" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4905 2.02168 11.3363C2.16356 9.18203 2.99721 7.13214 4.39828 5.49883C5.79935 3.86553 7.69279 2.72636 9.79619 2.24899C11.8996 1.77162 14.1003 1.98274 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<polyline points="22,4 12,14.01 9,11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</div>
		
		<h1>Meeting Completed!</h1>
		<p>Great job {user.name}! You've successfully completed your AI meeting .</p>
		
		<div class="completion-details">
			<p>You will receive detailed feedback on your performance via email soon.</p>
		</div>
		
		{#if showNewMeetingButton}
			<div class="action-section">
				<button class="new-meeting-btn" onclick={startNewMeeting}>
					Take New Meeting
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<polyline points="12,5 19,12 12,19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</button>
			</div>
		{/if}
	</div>
</div>

<style>
	.complete-screen {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		/*background: linear-gradient(135deg, #111827 0%, #1f2937 100%);*/
		color: white;
		padding: 20px;
	}
	
	.complete-content {
		text-align: center;
		max-width: 600px;
		padding: 60px 40px;
		border-radius: 20px;
		border: 1px solid #374151;
	    background: rgba(255, 255, 255, 0.1);
    	backdrop-filter: blur(20px);
	}
	
	.complete-icon {
		margin-bottom: 32px;
		color: #10b981;
		animation: checkmark 0.6s ease-in-out;
	}
	
	@keyframes checkmark {
		0% {
			transform: scale(0);
			opacity: 0;
		}
		50% {
			transform: scale(1.1);
		}
		100% {
			transform: scale(1);
			opacity: 1;
		}
	}
	
	h1 {
		font-size: 3rem;
		margin-bottom: 24px;
		color: #f9fafb;
		font-weight: 700;
		/*background: linear-gradient(135deg, #10b981, #3b82f6);*/
		background: white;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	
	p {
		font-size: 1.2rem;
		color: #d1d5db;
		margin-bottom: 24px;
		line-height: 1.6;
	}
	
	.completion-details {
		background: rgba(16, 185, 129, 0.1);
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: 12px;
		padding: 24px;
		margin: 32px 0;
	}
	
	.completion-details p {
		margin: 0;
		color: #10b981;
		font-weight: 500;
	}
	
	.quote {
		margin: 40px 0;
		padding: 24px;
		border-left: 4px solid #3b82f6;
		background: rgba(59, 130, 246, 0.1);
		border-radius: 0 8px 8px 0;
	}
	
	.quote p {
		margin: 0;
		font-size: 1.1rem;
		color: #93c5fd;
		font-style: italic;
	}
	
	.action-section {
		margin-top: 40px;
		animation: slideUp 0.5s ease-out;
	}
	
	@keyframes slideUp {
		from {
			transform: translateY(20px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}
	
	.new-meeting-btn {
		display: inline-flex;
		align-items: center;
		gap: 12px;
		padding: 16px 32px;
		/*background: linear-gradient(135deg, #3b82f6, #1d4ed8);*/
		background: linear-gradient(90deg, #621e40 0%, #792828 100%);
		color: white;
		border: none;
		border-radius: 12px;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		/*box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);*/
	}
	
	.new-meeting-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
		background: linear-gradient(135deg, #2563eb, #1e40af);
	}
	
	.new-meeting-btn:active {
		transform: translateY(0);
	}
	
	@media (max-width: 768px) {
		.complete-content {
			padding: 40px 20px;
			margin: 20px;
		}
		
		h1 {
			font-size: 2.5rem;
		}
		
		p {
			font-size: 1.1rem;
		}
		
		.new-meeting-btn {
			padding: 14px 28px;
			font-size: 1rem;
		}
	}
</style>