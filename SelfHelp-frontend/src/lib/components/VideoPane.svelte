<script lang="ts">
	import { onMount } from 'svelte';
	
	export let stream: MediaStream | null = null;
	export let label = '';
	export let isAI = false;
	export let showVisualizer = false;
	export let isThinking = false;
	export let avatarStream = null;
	
	let videoElement;
	let canvasElement;
	let canvasContext;
	let animationId;
	let aiVideoElement;
	
	onMount(() => {
		if (canvasElement) {
			canvasContext = canvasElement.getContext('2d');
		}
		
		return () => {
			if (animationId) {
				cancelAnimationFrame(animationId);
			}
		};
	});
	
	$: if (videoElement && stream) {
		videoElement.srcObject = stream;
	}

	$: if (aiVideoElement && avatarStream!= null) {
		aiVideoElement.srcObject = avatarStream;
		aiVideoElement.onloadedmetadata = () => {
			aiVideoElement.play().catch(console.error);
		};
	}
	
	function drawVisualizer() {
		if (canvasElement) {
			canvasContext = canvasElement.getContext('2d');
		}
		if (!canvasContext || !showVisualizer) return;
		
		const width = canvasElement.width;
		const height = canvasElement.height;
		
		canvasContext.clearRect(0, 0, width, height);
		canvasContext.fillStyle = '#4ade80';
		
		// Simple animated bars
		const barCount = 20;
		const barWidth = width / barCount;
		
		for (let i = 0; i < barCount; i++) {
			const barHeight = Math.random() * height * 0.8;
			canvasContext.fillRect(i * barWidth, height - barHeight, barWidth - 2, barHeight);
		}
		
		animationId = requestAnimationFrame(drawVisualizer);
	}
	
	$: if (showVisualizer && canvasContext) {
		drawVisualizer();
	} else if (animationId) {
		cancelAnimationFrame(animationId);
		animationId = null;
	}
</script>

<div class="video-pane">
	<div class="video-container">
		{#if isAI}
		<div class="ai-placeholder">
			<div class="ai-avatar">
					<video class="ai-heygen-avatar" bind:this={aiVideoElement} autoplay playsinline></video>
			</div>
			<span class="ai-label">AI Assistant</span>
			{#if isThinking}
				<div class="live-transcription">
							<p>Thinking ...</p>
				</div>
			{/if}
			</div>
		{:else}
			<video bind:this={videoElement} autoplay muted playsinline></video>
		{/if}
		
		{#if showVisualizer}
			<canvas bind:this={canvasElement} class="visualizer" width="200" height="60"></canvas>
		{/if}
	</div>
	
	{#if label}
		<div class="label">{label}</div>
	{/if}
</div>

<style>
	.video-pane {
		position: relative;
		background: #2a2a2a;
		border-radius: 12px;
		overflow: hidden;
		aspect-ratio: 12/15;
		display: flex;
		flex-direction: column;
	}
	
	.video-container {
		flex: 1;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	video {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	
	.ai-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: #9ca3af;
		height: 100%;
	}
	
	.ai-avatar {
		/*width: 80px;
		height: 80px;*/
		background: #374151;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 12px;
		color: #6b7280;
	}
	
	.ai-label {
		font-size: 14px;
		font-weight: 500;
	}
	.ai-heygen-avatar{
		aspect-ratio: 12/16;
	}

	.live-transcription{
		position: absolute;
		bottom: 0;
		text-align: center;
		width: 100%;
		background: rgba(0, 0, 0, 0.2);
		border-radius: 0 0 12px 12px;	
	}
	.live-transcription p{
		margin: 5px;
	}
	
	.visualizer {
		position: absolute;
		bottom: 10px;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(0, 0, 0, 0.5);
		border-radius: 6px;
		padding: 4px;
	}
	
	.label {
		position: absolute;
		top: 10px;
		left: 10px;
		background: rgba(0, 0, 0, 0.7);
		color: white;
		padding: 4px 8px;
		border-radius: 4px;
		font-size: 12px;
		font-weight: 500;
	}
</style>