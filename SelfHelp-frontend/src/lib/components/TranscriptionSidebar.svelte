<script lang="ts">
	import { transcription } from '../stores/meeting.js';
	
	export let isCollapsed = false;
	
	let transcriptContainer;
	let transcriptEntries = [];
	
	// Subscribe to transcription updates
	$: if ($transcription) {
		addTranscriptEntry($transcription);
	}
	
	function addTranscriptEntry(text, speaker = 'User') {
		if (text.trim()) {
			transcriptEntries = [...transcriptEntries, {
				id: Date.now(),
				speaker,
				text: text.trim(),
				timestamp: new Date().toLocaleTimeString()
			}];
			
			// Auto-scroll to bottom
			setTimeout(() => {
				if (transcriptContainer) {
					transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
				}
			}, 100);
		}
	}
	
	export function clearTranscript() {
		console.log('Clearing ....');
		transcriptEntries = [];
		transcription.set('');
	}
	
	function toggleCollapse() {
		isCollapsed = !isCollapsed;
	}
	
	// Export function to add AI responses
	export function addAIResponse(text) {
		addTranscriptEntry(text, 'AI');
	}
</script>

<div class="sidebar" class:collapsed={isCollapsed}>
	<div class="sidebar-header">
		<h3>Transcription</h3>
		<div class="header-controls">
			
			<!--
			<button class="clear-btn" on:click={clearTranscript} title="Clear transcript">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M19 7L18.1327 19.1425C18.0579 20.1891 17.187 21 16.1378 21H7.86224C6.81296 21 5.94208 20.1891 5.86732 19.1425L5 7M10 11V17M14 11V17M15 7V4C15 3.44772 14.5523 3 14 3H10C9.44772 3 9 3.44772 9 4V7M4 7H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		-->
			
			<button class="collapse-btn" on:click={toggleCollapse} title={isCollapsed ? 'Expand' : 'Collapse'}>
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d={isCollapsed ? "M9 18L15 12L9 6" : "M15 18L9 12L15 6"} stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		</div>
	</div>
	
	{#if !isCollapsed}
		<div class="transcript-container" bind:this={transcriptContainer}>
			{#if transcriptEntries.length === 0}
				<div class="empty-state">
					<p>Transcription will appear here...</p>
				</div>
			{:else}
				{#each transcriptEntries as entry (entry.id)}
					<div class="transcript-entry" class:ai={entry.speaker === 'AI'}>
						<div class="entry-header">
							<span class="speaker">{entry.speaker}</span>
							<span class="timestamp">{entry.timestamp}</span>
						</div>
						<div class="entry-text">{entry.text}</div>
					</div>
				{/each}
			{/if}
		</div>
	{/if}
</div>

<style>
	.sidebar {
		width: 350px;
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(20px);
		border-left: 1px solid rgba(255, 255, 255, 0.2);
		display: flex;
		flex-direction: column;
		transition: width 0.3s ease;
	}
	
	.sidebar.collapsed {
		width: 50px;
	}
	
	.sidebar-header {
		padding: 16px;
		border-bottom: 1px solid rgba(255, 255, 255, 0.2);
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: rgba(255, 255, 255, 0.05);
		backdrop-filter: blur(10px);
		background: linear-gradient(90deg, #621e40 0%, #792828 100%);
	}
	
	.sidebar.collapsed .sidebar-header {
		padding: 16px 12px;
		background: none;
	}
	
	h3 {
		color: #f9fafb;
		margin: 0;
		font-size: 16px;
		font-weight: 600;
	}
	
	.sidebar.collapsed h3 {
		display: none;
	}
	
	.header-controls {
		display: flex;
		gap: 8px;
	}
	
	.clear-btn,
	.collapse-btn {
		background: none;
		border: none;
		color: #9ca3af;
		cursor: pointer;
		padding: 4px;
		border-radius: 4px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s ease;
	}
	
	.clear-btn:hover,
	.collapse-btn:hover {
		color: #f9fafb;
		background: rgba(74, 222, 128, 0.2);
	}
	
	.transcript-container {
		flex: 1;
		overflow-y: auto;
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 12px;
		direction: rtl;
	}
	
	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: #fff;
		font-style: italic;
	}
	
	.transcript-entry {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 12px;
		padding: 12px;
		border-left: 3px solid #4ade80;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		direction: ltr;
	}
	
	.transcript-entry.ai {
		border-left-color: #a855f7;
		background: rgba(168, 85, 247, 0.1);
	}
	
	.entry-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}
	
	.speaker {
		font-weight: 600;
		color: #f9fafb;
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}
	
	.timestamp {
		font-size: 11px;
		color: #9ca3af;
	}
	
	.entry-text {
		color: #e5e7eb;
		line-height: 1.5;
		font-size: 14px;
	}
	
	/* Scrollbar styling */
	.transcript-container::-webkit-scrollbar {
		width: 6px;
	}
	
	.transcript-container::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.05);
	}
	
	.transcript-container::-webkit-scrollbar-thumb {
		background: rgba(74, 222, 128, 0.3);
		border-radius: 3px;
	}
	
	.transcript-container::-webkit-scrollbar-thumb:hover {
		background: rgba(74, 222, 128, 0.5);
	}
</style>