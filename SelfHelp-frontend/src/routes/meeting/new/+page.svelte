<script lang="ts">
	import type { PageData } from './$types';
	
	let { data }: { data: PageData } = $props();
	const { user } = data;
	console.log(data);

	import { PUBLIC_BACKEND_SERVER_URL } from '$env/static/public';	
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { transcription, isRecording, mediaStream, errorMessage, successMessage } from '$lib/stores/meeting.js';
	import { StreamingTranscriber } from "assemblyai";
	//import { RealtimeTranscriber } from 'assemblyai';
	
	import VideoPane from '$lib/components/VideoPane.svelte';
	import TranscriptionSidebar from '$lib/components/TranscriptionSidebar.svelte';
	import Error from '../../+error.svelte';

	let audioContext;
	let recordingStartTime: number;
	let recordingDuration = $state(0);
	let recordingInterval;
	let showSubmitButton: boolean = $state(false);
	let isSubmitting: boolean = $state(false);
	let permissionsGranted: boolean = $state(false);
	let connectionStatus: string = 'idle'; // idle, connecting, connected, stopped, error
	
	const MAX_RECORDING_TIME: number = 180; // 3 minutes in seconds

	let transComp;
	onMount(async () => {
		await initializeServices();
	});
	
	async function initializeServices() {
		try {
			
			// Request media permissions
			await requestPermissions();
			
			
		} catch (error) {
			console.error('Failed to initialize services:', error);
			errorMessage.set('Failed to connect to speech service. Please reload the page.');
			connectionStatus = 'error';
		}
	}
	
	async function requestPermissions() {

		
		try {
			const stream: MediaStream = await navigator.mediaDevices.getUserMedia({ 
				video: true, 
				audio: true 
			});
			
			mediaStream.set(stream);
			permissionsGranted = true;
			console.log('TRACKS',$mediaStream.getAudioTracks());
			
		} catch (error) {
			console.error('Permission denied:', error);
			errorMessage.set('Camera and microphone access required. Please enable permissions and reload.');
		}
	}
	
	function handleTranscription(text: string, formatted: boolean) {
		if (formatted) {
			transcription.update(current => current + ' ' + text);
		}
	}
	
	
	let transcriber: StreamingTranscriber | null = null;


	let finalTranscript: string = "";
	let penUltimate: string = $state("");

	let liveTranscript: string = $state("");


	async function setUpTranscriber(token: string){

		transcriber = new StreamingTranscriber({
			token,
			sampleRate: 16000,
			formatTurns: false,
		});

		//Set up event Listeners
		transcriber.on("open", ({ id, expires_at }) => console.log('Transcriber SESSION ID:', id, 'Expires at:', expires_at));
		
		transcriber.on("close", (code, reason) => {
			console.log('Transcriber Closed', code, reason)
			connectionStatus ='error';
		});


		transcriber.on("turn", ( transcript ) => {


			console.log(transcript);
			console.log('Live ... transcript:', transcript.transcript);
			console.info(`Live Transcript: ${liveTranscript}`);
			
			if (transcript.transcript ==""){
				console.log("transcription blank.... ");
				penUltimate +="\n"
				finalTranscript += penUltimate;
			}
			penUltimate = transcript.transcript;


			liveTranscript = penUltimate.substring(penUltimate.length-50);
		});


		transcriber.on("error", (error) => console.error('Error', error));

		//Connect
		await transcriber.connect();
	}

	function downsampleBuffer(buffer, originalSampleRate, targetSampleRate) {
			
		if (targetSampleRate === originalSampleRate) {
				return buffer;
			}

			const sampleRateRatio = originalSampleRate / targetSampleRate;
			const newLength = Math.round(buffer.length / sampleRateRatio);
			const result = new Int16Array(newLength);

			let offsetResult = 0;
			let offsetBuffer = 0;

			while (offsetResult < result.length) {
				const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
				// Average the samples in this range
				let sum = 0, count = 0;
				for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
				sum += buffer[i];
				count++;
				}
				result[offsetResult] = Math.max(-32768, Math.min(32767, (sum / count) * 32768));
				offsetResult++;
				offsetBuffer = nextOffsetBuffer;
			}

			return result;
	}

	function isSilent(buffer, threshold = 0.01) {
		let sumOfSquares = 0;
		for (let i = 0; i < buffer.length; i++) {
			sumOfSquares += buffer[i] * buffer[i];
		}
		const rms = Math.sqrt(sumOfSquares / buffer.length);
		
		//console.log("Current RMS:", rms); 
		return rms < threshold;
	}

	function listenToMe(){

		const source = audioContext.createMediaStreamSource($mediaStream);
		const processor = audioContext.createScriptProcessor(4096, 1, 1);

		source.connect(processor);
		processor.connect(audioContext.destination);

		processor.onaudioprocess = (event) => {

			if ($isRecording) {

				let float32Data = event.inputBuffer.getChannelData(0);
				
				if (isSilent(float32Data)) {
					//console.log('Silence detected, skipping API call.');
                	return; // Stop processing this chunk
            	}
				
				console.log('sending ....');
				const downsampled = downsampleBuffer(float32Data, audioContext.sampleRate, 16000);
				transcriber.sendAudio(downsampled.buffer);
			}
		};
			
	}
	
	async function startRecording() {

		if (!permissionsGranted || !$mediaStream) {
			errorMessage.set('Please enable camera and microphone permissions first.');
			return;
		}
		
		try {
			    //Get the temp streaming Key
				const response = await	fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/v1/assemblyaiToken`, {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' }
				});
				
				const authData = await response.json();
				if (!response.ok){
					console.log(authData.detail);
					throw new Error(authData.detail || 'Failed to streaming Token');
				}
			
				connectionStatus = 'connecting';
				const token = authData.token;
				console.log('TOKEN: ', token);


				await setUpTranscriber(token);
				
				console.log('Post Transcriber Setup ...');
				connectionStatus = 'connected';
				
				
				
				isRecording.set(true);
				recordingStartTime = Date.now();
				
				// Start recording timer
				recordingInterval = setInterval(() => {
					recordingDuration = Math.floor((Date.now() - recordingStartTime) / 1000);
					if (recordingDuration >= MAX_RECORDING_TIME) {
						stopRecording();
					}
				}, 1000);
				
				// Setup audio processing for AssemblyAI
				audioContext = new (window.AudioContext || window.webkitAudioContext)();
				if (audioContext.state === 'suspended') {
					console.log('Resuming ...');
					await audioContext.resume();
				}


				listenToMe();
			
			
		} catch (error) {
			console.error('Failed to start recording:', error);
			errorMessage.set('Failed to start recording. Please try again.');
			isRecording.set(false);
		}
	}
	
	async function stopRecording() {

		isRecording.set(false);
		showSubmitButton = true;
		connectionStatus = 'stopped';


		if(transcriber)
			await transcriber.close();
		
		if (recordingInterval) {
			clearInterval(recordingInterval);
			recordingInterval = null;
		}
		
		if (audioContext) {
			audioContext.close();
			audioContext = null;
		}

		console.log('penultimate:: ', penUltimate);
		finalTranscript+=penUltimate;

		if(finalTranscript.trim() !== ""){
			console.log('NOT BLANK');
			handleTranscription(finalTranscript, true);
		}

		console.log("FINAL: ", finalTranscript);
	}
	
	async function cancelRecording() {
		//transcription.set('');
		finalTranscript = "";
		penUltimate = "";
		await stopRecording();
		transComp.clearTranscript();
		showSubmitButton = false;
		recordingDuration = 0;
		connectionStatus ='idle';
		successMessage.set('Recording cancelled. You can start a new recording.');
		setTimeout(() => successMessage.set(''), 3000);
	}
	
	async function submitRequest() {
		if (!$transcription.trim()) {
			errorMessage.set('No transcription available. Please record something first.');
			return;
		}
		
		isSubmitting = true;
		
		try {
			const response = await fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/v1/meeting/new`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					transcript: $transcription.trim()
				})
			});
			
			const data = await response.json();
			
			if (response.ok) {
				successMessage.set('Meeting successfully scheduled!');
				showSubmitButton = false;
				// Show "Meet" button and navigate after a short delay
				setTimeout(() => {
					goto(`/meeting/${data.id}`);
				}, 1500);
			} else {
				throw new Error(data.message || 'Failed to schedule meeting');
			}
		} catch (error) {
			console.error('Failed to submit request:', error);
			errorMessage.set('Failed to schedule meeting. Please try again.');
			showSubmitButton = false; // Show redo button
		} finally {
			isSubmitting = false;
		}
	}
	
	function redoRecording() {
		window.location.reload();
	}
	
	function formatTime(seconds) {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

</script>

<svelte:head>
	<title>Let's Set you up !</title>
</svelte:head>



<div class="page-container">
	<div class="main-content">
		<div class="header-section">Let us know something about yourself !</div>
		<div class="video-section">
			<VideoPane 
				stream={$mediaStream} 
				label="You" 
				showVisualizer={false}
			/>

			{#if showSubmitButton}
				<div class="submit-section">
					<button 
						class="submit-btn" 
						disabled={isSubmitting}
						onclick={submitRequest}
					>
						{isSubmitting ? 'Submitting...' : 'Submit Request'}
					</button>
				</div>
			{:else if $errorMessage && !showSubmitButton && $transcription.trim()}
				<div class="submit-section">
					<button class="redo-btn" onclick={redoRecording}>
						Oops ... Try Again !
					</button>
				</div>
			{/if}
			
			
			{#if connectionStatus === 'connecting'}
				<div class="status-overlay">
					<div class="loading-spinner"></div>
					<p>Connecting to speech service...</p>
				</div>
			{:else if connectionStatus === 'error'}
				<div class="status-overlay error">
					<p>Connection failed. Please reload the page.</p>
				</div>
			{/if}
			{#if !permissionsGranted}
				<div class="status-overlay">
					<p>Please enable camera and microphone permissions</p>
				</div>
			{/if}
			{#if $isRecording}
				<div class="recording-info">
					<div class="recording-indicator">
						<div class="pulse"></div>
						{formatTime(recordingDuration)} / {formatTime(MAX_RECORDING_TIME)}
					</div>
				</div>
				<div class="live-transcription">
					<p>{liveTranscript}</p>
				</div>
			{/if}
		</div>
		
		<div class="controls">
			
			<!--Start Recording {permissionsGranted} - {connectionStatus} {$isRecording} -->
			<div class="button-row">
				<button aria-label="Start Recording" 
					class="control-btn start-btn" 
					disabled={!permissionsGranted || connectionStatus !== 'idle' || $isRecording}
					onclick={startRecording}
				>
					<svg
						class="cricle-btn"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
						>
						<path
							d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z"
							fill="currentColor"
						/>
						<path
							fill-rule="evenodd"
							clip-rule="evenodd"
							d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12Z"
							fill="currentColor"
						/>
						</svg>
				</button>
				
				<button aria-label="Stop Recording" class="control-btn stop-btn" disabled={!$isRecording} onclick={stopRecording} >
					<svg
					class="cricle-btn"
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					>
					<path d="M15 9H9V15H15V9Z" fill="currentColor" />
					<path
						fill-rule="evenodd"
						clip-rule="evenodd"
						d="M23 12C23 18.0751 18.0751 23 12 23C5.92487 23 1 18.0751 1 12C1 5.92487 5.92487 1 12 1C18.0751 1 23 5.92487 23 12ZM21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
						fill="currentColor"
					/>
					</svg>
				</button>
				
				<button	aria-label="Cancel Recording" class="control-btn cancel-btn" onclick={cancelRecording}>
					<svg
						class="cricle-btn"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
						>
						<path
							d="M5.33929 4.46777H7.33929V7.02487C8.52931 6.08978 10.0299 5.53207 11.6607 5.53207C15.5267 5.53207 18.6607 8.66608 18.6607 12.5321C18.6607 16.3981 15.5267 19.5321 11.6607 19.5321C9.51025 19.5321 7.58625 18.5623 6.30219 17.0363L7.92151 15.8515C8.83741 16.8825 10.1732 17.5321 11.6607 17.5321C14.4222 17.5321 16.6607 15.2935 16.6607 12.5321C16.6607 9.77065 14.4222 7.53207 11.6607 7.53207C10.5739 7.53207 9.56805 7.87884 8.74779 8.46777L11.3393 8.46777V10.4678H5.33929V4.46777Z"
							fill="currentColor"
						/>
						</svg>
				</button>
			</div>
		
		</div>
	</div>
	
	<TranscriptionSidebar bind:this={transComp}/>
</div>

{#if $errorMessage}
	<div class="message error-message">
		{$errorMessage}
		<button onclick={() => errorMessage.set('')}>×</button>
	</div>
{/if}

{#if $successMessage}
	<div class="message success-message">
		{$successMessage}
		<button onclick={() => successMessage.set('')}>×</button>
	</div>
{/if}

<style>
	.page-container {
		display: flex;
		height: 100vh;
		/*background: linear-gradient(135deg, #4ade80 0%, #22d3ee 25%, #a855f7 75%, #ec4899 100%);
		background-image: linear-gradient(146deg, rgba(44, 35, 109, 0.5) 0%, rgba(44, 35, 109, 0.5) 14.286%,rgba(64, 54, 108, 0.5) 14.286%, rgba(64, 54, 108, 0.5) 28.572%,rgba(83, 72, 106, 0.5) 28.572%, rgba(83, 72, 106, 0.5) 42.858%,rgba(103, 91, 105, 0.5) 42.858%, rgba(103, 91, 105, 0.5) 57.144%,rgba(123, 110, 103, 0.5) 57.144%, rgba(123, 110, 103, 0.5) 71.43%,rgba(142, 128, 102, 0.5) 71.43%, rgba(142, 128, 102, 0.5) 85.716%,rgba(162, 147, 100, 0.5) 85.716%, rgba(162, 147, 100, 0.5) 100.002%),linear-gradient(349deg, rgb(203, 4, 7) 0%, rgb(203, 4, 7) 14.286%,rgb(178, 9, 6) 14.286%, rgb(178, 9, 6) 28.572%,rgb(152, 13, 5) 28.572%, rgb(152, 13, 5) 42.858%,rgb(127, 18, 4) 42.858%, rgb(127, 18, 4) 57.144%,rgb(101, 22, 3) 57.144%, rgb(101, 22, 3) 71.43%,rgb(76, 27, 2) 71.43%, rgb(76, 27, 2) 85.716%,rgb(50, 31, 1) 85.716%, rgb(50, 31, 1) 100.002%);
		*/
		color: white;
	}
	
	.main-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		/*padding: 20px;
		border-radius: 20px;
		margin: 20px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		background: rgba(255, 255, 255, 0.05);*/
		gap: 20px;
		backdrop-filter: blur(10px);
	}

	.header-section{
		padding: 16px 24px;
		background: #1f2937;
		border-bottom: 1px solid #374151;
		display: flex;
		justify-content: space-between;
		align-items: center;
		border: 1px solid rgba(255, 255, 255, 0.1);
		margin: 10px 20px 5px;
		border-radius: 12px;
		background: linear-gradient(90deg, #621e40 0%, #792828 100%);
	}
	
	.video-section {
		flex: 1;
		position: relative;
		max-width: 600px;
		margin: 0 auto;
		width: 100%;
		max-height: 80%;
	}
	
	.status-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.8);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: white;
		border-radius: 12px;
	}
	
	.status-overlay.error {
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid #ef4444;
	}
	
	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 3px solid rgba(255, 255, 255, 0.2);
		border-top: 3px solid #4ade80;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 16px;
	}
	
	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	
	.controls {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
		max-width: 800px;
		margin: 0 auto;
		width: 100%;
	}
	
	.recording-info {
		/*display: flex;
		align-items: center;
		gap: 12px;*/
		position: absolute;
		top: 10px;
		right: 10px;
		background: rgba(0, 0, 0, 0.7);
		padding: 4px 8px;
		border-radius: 4px;
		font-size: 12px;
		font-weight: 500;
	}
	
	.recording-indicator {
		display: flex;
		align-items: center;
		gap: 8px;
		color: #ef4444;
		font-weight: 600;
	}
	
	.pulse {
		width: 12px;
		height: 12px;
		background: #ef4444;
		border-radius: 50%;
		animation: pulse 1s infinite;
	}
	
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.3; }
	}
	
	.button-row {
		display: flex;
		gap: 16px;
		flex-wrap: wrap;
		justify-content: center;
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
	.control-btn {
		border: none;
		border-radius: 50%;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		/*min-width: 140px;*/
	}
	.control-btn:disabled {
		color: white;
	}
	
	.start-btn {
		background: linear-gradient(135deg, #4ade80, #22d3ee);
		background: #10b981;
		color: white;
		box-shadow: 0 4px 15px rgba(74, 222, 128, 0.3);
	}
	
	.start-btn:hover:not(:disabled) {
		background: linear-gradient(135deg, #22c55e, #0891b2);
		background: #10b981;
		box-shadow: 0 6px 20px rgba(74, 222, 128, 0.4);
		transform: translateY(-2px);
	}
	
	.stop-btn {
		background: #ef4444;
		color: white;
	}
	
	.stop-btn:hover:not(:disabled) {
		background: #dc2626;
	}
	
	.cancel-btn {
		background: #6b7280;
		color: white;
	}
	
	.cancel-btn:hover {
		background: #4b5563;
	}
	
	.control-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.control-btn:active {
		box-shadow: 0 0 2px darkslategray;
		transform: translateY(2px);
	}
	.cricle-btn{
		width: 2.5rem;
		height: 100%;
	}
	
	.submit-section {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.8);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: white;
		border-radius: 12px;
		
	}
	
	.submit-btn,
	.redo-btn {
		padding: 16px 32px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		font-size: 16px;
	}
	
	.submit-btn {
		color: white;
		background: linear-gradient(90deg, #621e40 0%, #792828 100%);
	}
	
	.submit-btn:hover:not(:disabled) {
		
		background: linear-gradient(90deg, #621e40 0%, #792828 100%);
		box-shadow: 0 12px 35px rgba(193, 36, 36, 0.51);
		transform: translateY(-2px);
	}
	
	.redo-btn {
		background: #f59e0b;
		color: white;
	}
	
	.redo-btn:hover {
		background: #d97706;
	}
	
	.message {
		position: fixed;
		top: 20px;
		right: 20px;
		padding: 16px 20px;
		border-radius: 8px;
		display: flex;
		align-items: center;
		gap: 12px;
		z-index: 1000;
		max-width: 400px;
	}
	
	.error-message {
		background: #fef2f2;
		color: #991b1b;
		border: 1px solid #fecaca;
	}
	
	.success-message {
		background: #f0fdf4;
		color: #166534;
		border: 1px solid #bbf7d0;
	}
	
	.message button {
		background: none;
		border: none;
		font-size: 18px;
		cursor: pointer;
		color: inherit;
		opacity: 0.7;
	}
	
	.message button:hover {
		opacity: 1;
	}
</style>