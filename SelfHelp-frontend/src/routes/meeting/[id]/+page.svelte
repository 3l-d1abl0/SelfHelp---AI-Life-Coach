<script lang="ts">

	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
	const { user } = data;
	console.log('USER: ', user);

	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { transcription, isRecording, mediaStream, cameraEnabled, micEnabled, meetingStatus, errorMessage, successMessage } from '$lib/stores/meeting.js';
	
	import { AssemblyAIService } from '$lib/services/assemblyai.js';
	import { WebSocketService } from '$lib/services/websocketservice.js';
	
	import VideoPane from '$lib/components/VideoPane.svelte';
	import TranscriptionSidebar from '$lib/components/TranscriptionSidebar.svelte';
	
	import { PUBLIC_BACKEND_SERVER_URL } from '$env/static/public';	
	//import StreamingAvatar, {  AvatarQuality,  StreamingEvents,  TaskType } from "@heygen/streaming-avatar";
	import StreamingAvatar, {  AvatarQuality,  StreamingEvents,  TaskType } from '@heygen/streaming-avatar/lib/index.esm.js';
	
	let meetingId: string = $page.params.id;
	let assemblyService;
	let websocketService;
	let websocketServiceStatus = false;
	let audioContext;
	let transcriptSidebar;
	let meetingTimer;
	let meetingDuration = $state(0);
	let setupComplete: boolean = $state(false);
	let permissionsGranted: boolean = $state(false);
	let connectionStatus: string = $state('connecting');
	let aiGreeting : string = $state('');
	let isProcessingAI: boolean = $state(false);
	let sidebarCollapsed: boolean = $state(true);
	let defaultQuietDurationThreshold: number = 1500;
	let MEETING_DURATION : number = 300; // 5 minutes in seconds

	let heyGenStream = null;

	let finalTranscript = "";
	let penUltimate = "";

	let count =0;
	let avatar = null;
	let sessionData = null;
	
	onMount(async () => {
		meetingStatus.set('connecting');
		await initializeMeeting();
	});
	
	onDestroy(() => {
		cleanup();
	});
	
	async function initializeMeeting() {

		try {
			//Step 1: Connect to AssemblyAI
			await connectToAssemblyAI();
			connectionStatus = 'connected';
			
			// Step 2: Request permissions
			await requestPermissions();
			
			// Step 3: Start meeting
			const meetingTime = await startMeeting();
			await connectToWebSocketService(meetingId);

			//Step 4: Start Avatar
			await initializeAvatarSession();

			//throw new Error("Testing APIs");
			
			// All setup complete
			setupComplete = true;
			meetingStatus.set('active');
			
			// Wait 2 seconds then play AI greeting
			setTimeout(async () => {
				if (aiGreeting) {
					await playAIGreeting();
					startListening(defaultQuietDurationThreshold);
					startMeetingTimer(meetingTime);
				}
			}, 2000);
			
		} catch (error) {
			console.error('Failed to initialize meeting:', error.message);
			errorMessage.set(`Failed to start meeting. ${error.message}`);
			meetingStatus.set('error');

			if(error.message.includes('ended'))
				endMeeting();
		}
	}


	async function initializeAvatarSession(){

		const token = await fetchHeygenToken();
  		avatar = new StreamingAvatar({ token });

		avatar.on(StreamingEvents.STREAM_READY, handleStreamReady);
		avatar.on(StreamingEvents.STREAM_DISCONNECTED, handleStreamDisconnected);

		sessionData = await avatar.createStartAvatar({
			quality: AvatarQuality.Low,
			avatarName: "Wayne_20240711",
		});

		console.log("Session data:", sessionData);


	}

	function handleStreamReady(event) {

		console.log("EVENT: ", event.detail);
		console.warn("Strem started : handleStreamReady");
		heyGenStream = event.detail;
	}

	function handleStreamDisconnected() {
		console.warn("Stream disconnected");
		heyGenStream = null;
	}

	async function fetchHeygenToken(){
		try {
			const response = await fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/v1/heygenToken`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			
			const data = await response.json();
			if (response.ok) {
				console.log('Heygen Token: ', data.token);

				return data.token;
			} else {
				console.error('Error fetching Heygen Token:', data.detail);
				throw new Error(data.detail);
				
			}
		} catch (error) {
			console.log("ERROR: fetchHeygenToken : ", error.message);
			throw new Error(error.message);
		}
	}

	
	
	async function connectToAssemblyAI() {

		assemblyService = new AssemblyAIService();
		assemblyService.onTranscription = handleTranscription;
		assemblyService.onError = handleAssemblyError;
		assemblyService.onConnect = () => {
			connectionStatus = 'connected';
			console.log("connectionStatus: ", connectionStatus);
		};
		
		await assemblyService.connect();
	}
	
	async function handleTranscription(text: string) {

		console.log('TRANSCRIPTION: ', text);
		if (text=="") {
			console.log("transcription blank.... ");
			penUltimate +="\n"
			finalTranscript += penUltimate;
		}
		penUltimate = text;
	}

	function handleAssemblyError(error) {
		console.error('AssemblyAI error:', error);
		errorMessage.set('Speech service error occurred.');
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


	async function connectToWebSocketService(meetingId: string){

		websocketService = new WebSocketService(meetingId);
		//console.log(websocketService);

		websocketService.onConnect = () => {
			websocketServiceStatus = true;
			console.log('websocketServiceStatus: ', websocketServiceStatus);
		};

		websocketService.onInitiation = (initMessage) => {
			aiGreeting = initMessage;
			console.log(aiGreeting);
		};

		websocketService.onAIMentorMessage = (message) =>{

			if (avatar)
				avatar.speak({ text: message, task_type: "repeat", });
			
			if (transcriptSidebar) {
					console.log('adding to TranscriptSidebar ...');
					transcriptSidebar.addAIResponse(message);
			}
			console.log("AI Says: ", message);
		}
		
		await websocketService.connect();
	}
	

	
	async function startMeeting() {

		try {
			const response = await fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/v1/meeting/start`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					meetingId: meetingId
				})
			});
			
			const data = await response.json();
			console.log('Mentor Response: ', response.status);
			if (response.ok) {

				if(data.status === "meeting_started"){
					console.log("Meeting Stated : ",data.detail);
					return parseInt(data.remaining_seconds);
				}else if (data.status==="meeting_ended"){
					console.log("Meeting Ended :", data);
					throw new Error(data.detail);
				}else if (data.status == "meeting_ongoing"){
					console.log("Meeting Ongoing : ",data.detail);
					return parseInt(data.remaining_seconds);
				}	
			} else {

				if (response.status === 409) {
					console.error('Meeting concluded:', data.detail);
					throw new Error(data.detail);
				}
			}
		} catch (error) {
			console.log("ERROR: startMeeting : ", error.message);
			//throw new Error('Failed to connect to meeting service');
			throw new Error(error.message);
		}
	}
	
	async function playAIGreeting() {
		
		try {

			if (avatar)
				avatar.speak({ text: aiGreeting, task_type: "repeat", });

			// Add AI greeting to transcript
			if (transcriptSidebar) {
				console.log('adding to TranscriptSidebar ...');
				transcriptSidebar.addAIResponse(aiGreeting);
			}
			
			console.log('Playing mentor audio ...');
		} catch (error) {
			console.error('Failed to play AI greeting:', error);
		}
	}
	
	async function startListening(pauseTime: number) {
		if (!permissionsGranted || !$mediaStream) return;
		
		try {

			isRecording.set(true);

			let quietTimer = 0;
			let isSpeaking = false;
			let audioBufferQueue = []; 
			
			const quietDurationThreshold = pauseTime;
			const speakingThreshold = 0.02;
			
			// Setup audio processing for AssemblyAI
			audioContext = new (window.AudioContext || window.webkitAudioContext)();
			if (audioContext.state === 'suspended') {
				console.log('Resuming...');
				await audioContext.resume();
			}

			const source = audioContext.createMediaStreamSource($mediaStream);
			const processor = audioContext.createScriptProcessor(4096, 1, 1);
			
			function downsampleBuffer(buffer, originalSampleRate, targetSampleRate) {
				// Your existing downsample function, no changes needed here.
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

			
			function calculateRMS(buffer) {
				let sumOfSquares = 0;
				for (let i = 0; i < buffer.length; i++) {
						const sample = buffer[i];
						sumOfSquares += sample * sample;
					}
					return Math.sqrt(sumOfSquares / buffer.length);
			}		
			
			
			source.connect(processor);
			processor.connect(audioContext.destination);
			
			processor.onaudioprocess = (event) => {
				
				if ($isRecording && $micEnabled) {
					
					
					const float32Data = event.inputBuffer.getChannelData(0);
            
					// Check the volume of the current audio chunk
					const rms = calculateRMS(float32Data);
					
					// Add the current audio chunk to the queue
					const downsampled = downsampleBuffer(float32Data, audioContext.sampleRate, 16000);
					//console.log(downsampled);
					//audioBufferQueue.push(downsampled);

					//console.log(rms," ", speakingThreshold);

					console.log('CALLING assemblyService');
					assemblyService.sendAudio(downsampled.buffer);

					if (rms > speakingThreshold) {
						// A speaking sound is detected
						if (!isSpeaking) {
							isSpeaking = true;
							console.log('Speaker is speaking. Resetting quiet timer.');
						}
						quietTimer = 0; // Reset the quiet timer
					} else {
						
						// Audio is below the threshold and if User was Speaking
						if (isSpeaking) {
							// Accumulate time when sound is below threshold
							const bufferDuration = event.inputBuffer.duration * 1000; // in milliseconds
							quietTimer += bufferDuration;
							
							if (quietTimer >= quietDurationThreshold) {
								console.log('CALLING assemblyService');
								console.log("CALLED AGAIN !!!");
								assemblyService.sendAudio(downsampled.buffer);
								setTimeout(() => {
									isSpeaking = false;
									console.log('Quiet moment reached. Declaring speaker quiet.');
									
									
									//send
									if(isProcessingAI == false){
										
										isProcessingAI = true;
										sendToMentor();
									}
								 }, 200); // Small delay to catch final words
							}
						}
					}//else
					
					//send audio for transcription
					//console.log('Sending for Transscription ...');
					//console.log(assemblyService);
					//assemblyService.sendAudio(downsampled.buffer);
					
					
					
					
				}
			};
			
			
		} catch (error) {
			console.error('Failed to start listening:', error);
		}
	}
	
	function startMeetingTimer(timeInSeconds) {
		MEETING_DURATION = timeInSeconds;
		meetingTimer = setInterval(() => {
			meetingDuration++;
			if (meetingDuration >= MEETING_DURATION) {
				endMeeting();
			}
		}, 1000);
	}	
	
	function  sendText(){
		count++;
		sendToMentor(`Send Message: ${count}`);
	}
	
	async function sendToMentor(message="DEF"){

		if(message == "DEF"){
			console.log('PEN: ', penUltimate);
			console.log('FINAL: ', finalTranscript);

			finalTranscript+=penUltimate.trim();
			if(finalTranscript.trim()){
			//if(finalTranscript.trim() && penUltimate.trim()){

				let userQuery = finalTranscript.trim();
				transcription.set(userQuery);
				console.log('Sending to Mentor .... ', userQuery);				

				penUltimate = "";
				finalTranscript ="";

				await websocketService.askMentor(userQuery);
			}else{
				console.log("NOT SENT !");
			}
			
			isProcessingAI = false;
		}else{
			transcription.set(message);
			console.log('Custom message to Mentor .... '+message);
		}

	}
	async function sendToAI(userText) {	
		
		
		try {
			const response = await fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/meeting/${meetingId}`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					user_input: userText
				})
			});
			
			const data = await response.json();
			
			if (response.ok) {
				const aiResponse = data.ai_response;
				
				// Add to transcript
				if (transcriptSidebar) {
					transcriptSidebar.addAIResponse(aiResponse);
				}
				
			}
		} catch (error) {
			console.error('Failed to get AI response:', error);
		} finally {
			isProcessingAI = false;
		}
	}
	
	function toggleCamera() {
		cameraEnabled.update(enabled => {
			const newEnabled = !enabled;
			if ($mediaStream) {
				const videoTracks = $mediaStream.getVideoTracks();
				videoTracks.forEach(track => {
					track.enabled = newEnabled;
				});
			}
			return newEnabled;
		});
	}
	
	function toggleMicrophone() {
		micEnabled.update(enabled => {
			const newEnabled = !enabled;
			if ($mediaStream) {
				const audioTracks = $mediaStream.getAudioTracks();
				audioTracks.forEach(track => {
					track.enabled = newEnabled;
				});
			}
			return newEnabled;
		});
	}

	async function stopMeeting() {
		try {
			const response = await fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/v1/meeting/stop`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					meetingId: meetingId
				})
			});
			
			const data = await response.json();
			console.log('Mentor Response: ', response.status);
			if (response.ok) {
					console.log("Meeting Ended : ",data.detail);
			} else {
					console.error('Error while ending meeting :', data.detail);
					throw new Error(data.detail);
			}

		} catch (error) {
			console.log("ERROR: stopMeeting : ", error.message);
			//throw new Error('Failed to connect to meeting service');
			throw new Error(error.message);
		}
	}
	
	async function endMeeting() {
		// Show thank you message
		await stopMeeting();

		if(avatar)
			await avatar.stopAvatar();
		
		heyGenStream = null;
		avatar = null;
		meetingStatus.set('ended');
		cleanup();
		
		setTimeout(() => {
			goto('/meeting/complete');
		}, 3000);
	}
	
	function cleanup() {
		if (meetingTimer) {
			clearInterval(meetingTimer);
			meetingTimer = null;
		}
		
		if (audioContext) {
			audioContext.close();
			audioContext = null;
		}
		
		if (assemblyService) {
			assemblyService.terminate();
		}
		
		if ($mediaStream) {
			$mediaStream.getTracks().forEach(track => track.stop());
			mediaStream.set(null);
		}
		
		isRecording.set(false);
	}
	
	function formatTime(seconds) {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}
</script>

<svelte:head>
	<title>AI Meeting - {meetingId}</title>
</svelte:head>

{#if !setupComplete}
	<div class="setup-screen">
		<div class="setup-content">
			<div class="setup-icon">
			<!--
				<svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M15.5 14H20.5L22 15.5V18.5L20.5 20H15.5L14 18.5V15.5L15.5 14Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M8.5 14H13.5L15 15.5V18.5L13.5 20H8.5L7 18.5V15.5L8.5 14Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			-->
			</div>
			<h1>Meeting is starting soon</h1>
			<p>Setting up your AI buddy and preparing the environment...</p>
			
			<div class="setup-progress">
				<div class="progress-item" class:completed={connectionStatus === 'connected'}>
					<div class="progress-icon">
						{#if connectionStatus === 'connected'}
							✓
						{:else}
							<div class="spinner"></div>
						{/if}
					</div>
					<span>Connecting to speech service</span>
				</div>
				
				<div class="progress-item" class:completed={permissionsGranted}>
					<div class="progress-icon">
						{#if permissionsGranted}
							✓
						{:else}
							<div class="spinner"></div>
						{/if}
					</div>
					<span>Setting up camera and microphone</span>
				</div>
				
				<div class="progress-item" class:completed={aiGreeting}>
					<div class="progress-icon">
						{#if aiGreeting}
							✓
						{:else}
							<div class="spinner"></div>
						{/if}
					</div>
					<span>Preparing AI assistant</span>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="meeting-screen">

		<div class="left-column">
			<div class="meeting-header">
				<div class="meeting-info">
					<h2>AI Meeting Session</h2>
					<div class="meeting-timer">
						{formatTime(meetingDuration)} / {formatTime(MEETING_DURATION)}
					</div>
				</div>
			</div>
			
			<div class="meeting-content">
				<div class="video-grid">
					<VideoPane 
						avatarStream = {heyGenStream}
						isAI={true}
						label="AI Mentor"
						isThinking={isProcessingAI}
					/>
					
					<VideoPane 
						stream={$cameraEnabled ? $mediaStream : null}
						label={user.name} 
						showVisualizer={false}
					/>
					
				</div>
				
				<div class="meeting-controls">
					<button 
						class="control-btn camera-btn"
						class:active={$cameraEnabled}
						onclick={toggleCamera}
						title={$cameraEnabled ? 'Turn camera off' : 'Turn camera on'}
					>
						<svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<g>
								<path d="M0 0h24v24H0z" fill="none"/>
							{#if $cameraEnabled}
								<path d="M9.828 5l-2 2H4v12h16V7h-3.828l-2-2H9.828zM9 3h6l2 2h4a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h4l2-2zm3 15a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11zm0-2a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z" fill="currentColor"/>
							{:else}
								<path d="M19.586 21H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h.586L1.393 2.808l1.415-1.415 19.799 19.8-1.415 1.414L19.586 21zm-14-14H4v12h13.586l-2.18-2.18A5.5 5.5 0 0 1 7.68 9.094L5.586 7zm3.524 3.525a3.5 3.5 0 0 0 4.865 4.865L9.11 10.525zM22 17.785l-2-2V7h-3.828l-2-2H9.828l-.307.307-1.414-1.414L9 3h6l2 2h4a1 1 0 0 1 1 1v11.786zM11.263 7.05a5.5 5.5 0 0 1 6.188 6.188l-2.338-2.338a3.515 3.515 0 0 0-1.512-1.512l-2.338-2.338z" fill="currentColor"/>
							{/if}
							</g>
						</svg>
						<!--Camera {$cameraEnabled ? 'ON' : 'OFF'} -->
					</button>
					
					<button 
						class="control-btn mic-btn"
						class:active={$micEnabled}
						onclick={toggleMicrophone}
						title={$micEnabled ? 'Mute microphone' : 'Unmute microphone'}
					>

						<svg height="40" viewBox="0 0 512 512" width="40" xmlns="http://www.w3.org/2000/svg">
							{#if $micEnabled}
								<path d="M448,256c0-106-86-192-192-192S64,150,64,256s86,192,192,192S448,362,448,256Z" 
										style="fill:none;stroke:currentColor;stroke-miterlimit:10;stroke-width:32px"/>
								<line style="fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px" 
										x1="224" x2="288" y1="368" y2="368"/>
								<path d="M336,224.3v23.92c0,39.42-40.58,71.48-80,71.48h0c-39.42,0-80-32.06-80-71.48V224.3" 
										style="fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px"/>
								<line style="fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px" 
										x1="256" x2="256" y1="320" y2="368"/>
								<rect height="160" rx="48" ry="48" width="96" x="208" y="128" 
										style="fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;stroke-width:32px"/>
							{:else}
								<path d="M256,464C141.31,464,48,370.69,48,256S141.31,48,256,48s208,93.31,208,208S370.69,464,256,464Zm0-384C159,80,80,159,80,256S159,432,256,432s176-78.95,176-176S353.05,80,256,80Z" 
										fill="currentColor"/>
								<path d="M352,369a15.93,15.93,0,0,1-11.84-5.24l-192-210a16,16,0,0,1,23.68-21.52l192,210A16,16,0,0,1,352,369Z" 
										fill="currentColor"/>
								<path d="M352,248.22v-23.8a16.3,16.3,0,0,0-13.64-16.24C328.48,206.7,320,214.69,320,224.3v23.92a43.35,43.35,0,0,1-3.07,15.91,4,4,0,0,0,.76,4.16l19.19,21.1a2,2,0,0,0,3.19-.3A77.12,77.12,0,0,0,352,248.22Z" 
										fill="currentColor"/>
								<path d="M304,240V176a48.14,48.14,0,0,0-48-48h0a48.08,48.08,0,0,0-41,23.1,4,4,0,0,0,.47,4.77l84.42,92.86a2,2,0,0,0,3.46-1A47.84,47.84,0,0,0,304,240Z" 
										fill="currentColor"/>
								<path d="M246.57,285.2l-36.46-40.11a1,1,0,0,0-1.74.8,48.26,48.26,0,0,0,37.25,41A1,1,0,0,0,246.57,285.2Z" 
										fill="currentColor"/>
								<path d="M287.55,352H272V334.26a100.33,100.33,0,0,0,12.53-3.06,2,2,0,0,0,.89-3.26l-21.07-23.19a3.94,3.94,0,0,0-3.29-1.29c-1.69.15-3.39.24-5.06.24-36,0-64-29.82-64-55.48V224.4A16.26,16.26,0,0,0,176.39,208,15.91,15.91,0,0,0,160,224v24.22c0,23.36,10.94,45.61,30.79,62.66A103.71,103.71,0,0,0,240,334.26V352H224.45c-8.61,0-16,6.62-16.43,15.23A16,16,0,0,0,224,384h64a16,16,0,0,0,16-16.77C303.58,358.62,296.16,352,287.55,352Z" 
										fill="currentColor"/>
							{/if}
						</svg>
						<!--Mic {$micEnabled ? 'ON' : 'OFF'} -->
					</button>
					
					<button 
						class="control-btn end-btn"
						onclick={endMeeting}
						title="End meeting"
					>


						<svg width="25" height="25" viewBox="0 0 15 15" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
						<title>End meeting</title>
						<defs></defs>
						<g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
							<g id="Dribbble-Light-Preview" transform="translate(-103.000000, -7321.000000)" fill="currentColor">
							<g id="icons" transform="translate(56.000000, 160.000000)">
								<path d="M61.7302966,7173.99596 C61.2672966,7175.40296 59.4532966,7176.10496 58.1572966,7175.98796 C56.3872966,7175.82796 54.4612966,7174.88896 52.9992966,7173.85496 C50.8502966,7172.33496 48.8372966,7169.98396 47.6642966,7167.48896 C46.8352966,7165.72596 46.6492966,7163.55796 47.8822966,7161.95096 C48.3382966,7161.35696 48.8312966,7161.03996 49.5722966,7161.00296 C50.6002966,7160.95296 50.7442966,7161.54096 51.0972966,7162.45696 C51.3602966,7163.14196 51.7112966,7163.84096 51.9072966,7164.55096 C52.2742966,7165.87596 50.9912966,7165.93096 50.8292966,7167.01396 C50.7282966,7167.69696 51.5562966,7168.61296 51.9302966,7169.09996 C52.6632966,7170.05396 53.5442966,7170.87696 54.5382966,7171.50296 C55.1072966,7171.86196 56.0262966,7172.50896 56.6782966,7172.15196 C57.6822966,7171.60196 57.5872966,7169.90896 58.9912966,7170.48196 C59.7182966,7170.77796 60.4222966,7171.20496 61.1162966,7171.57896 C62.1892966,7172.15596 62.1392966,7172.75396 61.7302966,7173.99596 C61.4242966,7174.92396 62.0362966,7173.06796 61.7302966,7173.99596" id="call-[#192]">
								</path>
							</g>
							</g>
						</g>
						</svg>
						<!--End Call-->
					</button>
				
					<button class="control-btn" onclick={sendText} title= "Send TXT">
						<svg width="30" height="30" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><title/><g data-name="1" id="_1"><path d="M373.43,444.44a15,15,0,0,1-11.29-5.12l-47.93-54.77A236,236,0,0,1,255.13,392C202,392,151.85,374.7,114,343.35c-38.63-32-59.91-74.85-59.91-120.59S75.41,134.2,114,102.18C151.85,70.83,202,53.56,255.13,53.56s103.28,17.27,141.1,48.62c38.63,32,59.9,74.85,59.9,120.58,0,48.82-24.57,94.6-67.7,126.72v80a15,15,0,0,1-15,15Zm-54.17-91.88a15,15,0,0,1,11.29,5.12l27.88,31.85V341.77A15,15,0,0,1,365,329.38c38.88-26.59,61.17-65.45,61.17-106.62,0-76.75-76.71-139.2-171-139.2s-171,62.45-171,139.2S160.84,362,255.13,362a205.07,205.07,0,0,0,59.76-8.76A14.93,14.93,0,0,1,319.26,352.56Z"/><path d="M201.49,264c-.49,0-1,0-1.47-.07s-1-.13-1.46-.22-1-.22-1.42-.36-.94-.31-1.39-.5-.89-.4-1.32-.63a14.6,14.6,0,0,1-1.27-.75c-.4-.27-.8-.56-1.18-.87s-.75-.65-1.1-1-.68-.72-1-1.1-.6-.78-.87-1.18a14.6,14.6,0,0,1-.75-1.27q-.35-.65-.63-1.32a14.17,14.17,0,0,1-.49-1.38,12,12,0,0,1-.36-1.43,12.1,12.1,0,0,1-.22-1.45,14.68,14.68,0,0,1-.08-1.48,14.32,14.32,0,0,1,.08-1.47,15.21,15.21,0,0,1,.58-2.89,14.17,14.17,0,0,1,.49-1.38q.29-.67.63-1.32a14.6,14.6,0,0,1,.75-1.27c.27-.4.56-.8.87-1.18s.65-.75,1-1.1.72-.68,1.1-1,.78-.6,1.18-.87a12.45,12.45,0,0,1,1.27-.75q.65-.34,1.32-.63a13.53,13.53,0,0,1,1.39-.5c.46-.14.94-.26,1.42-.36s1-.17,1.46-.22a14.54,14.54,0,0,1,2.95,0c.48.05,1,.13,1.45.22s1,.22,1.43.36a14.25,14.25,0,0,1,1.38.5c.45.19.9.4,1.33.63a13.48,13.48,0,0,1,1.26.75,14.34,14.34,0,0,1,1.18.87c.38.31.75.65,1.1,1s.68.72,1,1.1.6.78.87,1.18a14.6,14.6,0,0,1,.75,1.27q.34.65.63,1.32c.19.45.35.92.5,1.38s.26,1,.36,1.43a14.46,14.46,0,0,1,.29,2.93,14.66,14.66,0,0,1-.07,1.48,14.51,14.51,0,0,1-.22,1.45c-.1.48-.22,1-.36,1.43s-.31.93-.5,1.38-.4.89-.63,1.32a14.6,14.6,0,0,1-.75,1.27c-.27.4-.56.8-.87,1.18s-.65.75-1,1.1-.72.68-1.1,1a14.34,14.34,0,0,1-1.18.87q-.62.4-1.26.75c-.43.23-.88.44-1.33.63s-.92.35-1.38.5-.95.26-1.43.36-1,.17-1.45.22S202,264,201.49,264Z"/><path d="M312.5,264a14.46,14.46,0,0,1-1.47-.07c-.49-.05-1-.13-1.46-.22s-1-.22-1.42-.36-.93-.31-1.38-.5-.9-.4-1.33-.63A15.58,15.58,0,0,1,303,260.6c-.38-.31-.75-.65-1.09-1a14.67,14.67,0,0,1-1-1.1c-.31-.38-.61-.78-.88-1.18a14.6,14.6,0,0,1-.75-1.27q-.34-.65-.63-1.32c-.18-.45-.35-.92-.49-1.38a12,12,0,0,1-.36-1.43,15.49,15.49,0,0,1-.3-2.93,14.68,14.68,0,0,1,.08-1.48,14.51,14.51,0,0,1,.22-1.45,12,12,0,0,1,.36-1.43c.14-.46.31-.93.49-1.38s.4-.89.63-1.32a14.6,14.6,0,0,1,.75-1.27c.27-.4.57-.8.88-1.18a14.67,14.67,0,0,1,1-1.1c.34-.34.71-.68,1.09-1a15.58,15.58,0,0,1,2.45-1.62c.43-.23.87-.44,1.33-.63s.91-.35,1.38-.5.94-.26,1.42-.36,1-.17,1.46-.22a16.15,16.15,0,0,1,3,0c.48.05,1,.13,1.45.22s1,.22,1.43.36.93.31,1.38.5.9.4,1.33.63.85.48,1.26.75a12.82,12.82,0,0,1,1.18.87c.38.31.75.65,1.1,1s.68.72,1,1.1.6.78.87,1.18a14.69,14.69,0,0,1,.76,1.27c.22.43.44.87.62,1.32a14.25,14.25,0,0,1,.5,1.38c.14.47.26,1,.36,1.43s.17,1,.22,1.45a14.66,14.66,0,0,1,.07,1.48,14.33,14.33,0,0,1-.07,1.47c-.05.49-.13,1-.22,1.46s-.22,1-.36,1.43a14.25,14.25,0,0,1-.5,1.38c-.18.45-.4.89-.62,1.32a14.69,14.69,0,0,1-.76,1.27c-.27.4-.56.8-.87,1.18s-.65.75-1,1.1-.72.68-1.1,1a12.82,12.82,0,0,1-1.18.87q-.61.4-1.26.75c-.43.23-.88.44-1.33.63s-.92.35-1.38.5-.95.26-1.43.36-1,.17-1.45.22A14.66,14.66,0,0,1,312.5,264Z"/><path d="M257,264a15.11,15.11,0,0,1-10.61-4.39,14.67,14.67,0,0,1-1-1.1c-.31-.38-.6-.78-.88-1.18s-.52-.83-.75-1.27a13.2,13.2,0,0,1-.62-1.32,14.25,14.25,0,0,1-.5-1.38c-.14-.47-.26-1-.36-1.43a14.51,14.51,0,0,1-.22-1.45,15.68,15.68,0,0,1,0-3,14.51,14.51,0,0,1,.22-1.45c.1-.48.22-1,.36-1.43a14.25,14.25,0,0,1,.5-1.38,13.2,13.2,0,0,1,.62-1.32c.23-.44.49-.86.75-1.27s.57-.8.88-1.18a14.67,14.67,0,0,1,1-1.1,15.12,15.12,0,0,1,12.08-4.32c.49.05,1,.13,1.46.22s.95.22,1.42.36.93.31,1.38.5.9.4,1.33.63a15.58,15.58,0,0,1,2.45,1.62c.38.31.75.65,1.09,1a14.67,14.67,0,0,1,1,1.1c.31.38.61.78.88,1.18a14.6,14.6,0,0,1,.75,1.27q.34.65.63,1.32c.18.45.35.92.49,1.38a12,12,0,0,1,.36,1.43,14.51,14.51,0,0,1,.22,1.45,13.73,13.73,0,0,1,0,3,14.51,14.51,0,0,1-.22,1.45,12,12,0,0,1-.36,1.43c-.14.46-.31.93-.49,1.38s-.4.89-.63,1.32a14.6,14.6,0,0,1-.75,1.27c-.27.4-.57.8-.88,1.18a14.67,14.67,0,0,1-1,1.1c-.34.34-.71.67-1.09,1a15.58,15.58,0,0,1-2.45,1.62c-.43.23-.88.44-1.33.63s-.91.35-1.38.5-1,.26-1.42.36-1,.17-1.46.22A14.46,14.46,0,0,1,257,264Z"/></g></svg>
						
					</button>
				
				</div>
			</div>
		</div>
		
		<TranscriptionSidebar bind:this={transcriptSidebar} isCollapsed={sidebarCollapsed} user={user.name} />
	</div>
{/if}

{#if $meetingStatus === 'ended'}
	<div class="end-screen">
		<div class="end-content">
			<div class="end-icon">
				<svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4905 2.02168 11.3363C2.16356 9.18203 2.99721 7.13214 4.39828 5.49883C5.79935 3.86553 7.69279 2.72636 9.79619 2.24899C11.8996 1.77162 14.1003 1.98274 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<polyline points="22,4 12,14.01 9,11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<h1>Thank You!</h1>
			<p>Your meeting has ended successfully. You will receive a detailed report later.</p>
		</div>
	</div>
{/if}

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
	.setup-screen,
	.end-screen {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		background: #111827;
		color: white;
	}
	
	.setup-content,
	.end-content {
		text-align: center;
		max-width: 500px;
		padding: 40px;
	}
	
	.setup-icon,
	.end-icon {
		margin-bottom: 24px;
		color: #3b82f6;
	}
	
	h1 {
		font-size: 2.5rem;
		margin-bottom: 16px;
		color: #f9fafb;
	}
	
	p {
		font-size: 1.1rem;
		color: #9ca3af;
		margin-bottom: 32px;
	}
	
	.setup-progress {
		display: flex;
		flex-direction: column;
		gap: 16px;
		text-align: left;
	}
	
	.progress-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px;
		background: #1f2937;
		border-radius: 8px;
		transition: all 0.3s ease;
	}
	
	.progress-item.completed {
		background: #065f46;
		color: #10b981;
	}
	
	.progress-icon {
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: bold;
	}
	
	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid #374151;
		border-top: 2px solid #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	
	.meeting-screen {
		display: flex;
		/*flex-direction: column;*/
		height: 100vh;
		/*background: #111827;
		background: linear-gradient(135deg, #4ade80 0%, #22d3ee 25%, #a855f7 75%, #ec4899 100%);
		background-image: linear-gradient(146deg, rgba(44, 35, 109, 0.5) 0%, rgba(44, 35, 109, 0.5) 14.286%,rgba(64, 54, 108, 0.5) 14.286%, rgba(64, 54, 108, 0.5) 28.572%,rgba(83, 72, 106, 0.5) 28.572%, rgba(83, 72, 106, 0.5) 42.858%,rgba(103, 91, 105, 0.5) 42.858%, rgba(103, 91, 105, 0.5) 57.144%,rgba(123, 110, 103, 0.5) 57.144%, rgba(123, 110, 103, 0.5) 71.43%,rgba(142, 128, 102, 0.5) 71.43%, rgba(142, 128, 102, 0.5) 85.716%,rgba(162, 147, 100, 0.5) 85.716%, rgba(162, 147, 100, 0.5) 100.002%),linear-gradient(349deg, rgb(203, 4, 7) 0%, rgb(203, 4, 7) 14.286%,rgb(178, 9, 6) 14.286%, rgb(178, 9, 6) 28.572%,rgb(152, 13, 5) 28.572%, rgb(152, 13, 5) 42.858%,rgb(127, 18, 4) 42.858%, rgb(127, 18, 4) 57.144%,rgb(101, 22, 3) 57.144%, rgb(101, 22, 3) 71.43%,rgb(76, 27, 2) 71.43%, rgb(76, 27, 2) 85.716%,rgb(50, 31, 1) 85.716%, rgb(50, 31, 1) 100.002%);
		*/
		color: white;
	}
	.left-column{
			display: flex;
			flex-direction: column;
			flex: 1; /* Takes available space */
			/*padding: 10px;*/
			backdrop-filter: blur(10px);
	}
	
	.meeting-header {
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
	
	.meeting-info{
		display: flex;
		flex-direction: row;
		gap: 10px;
	}

	.meeting-info h2 {
		margin: 0;
		font-size: 1.25rem;
		color: #f9fafb;
	}
	
	.meeting-timer {
		font-size: 0.9rem;
		color: #9ca3af;
		margin-top: 4px;
	}
	
	.meeting-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 20px;
		gap: 20px;
	}
	
	.video-grid {
		/*flex: 1;*/
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}
	
	.meeting-controls {
		display: flex;
		justify-content: center;
		gap: 16px;
		/*padding: 16px;*/
	}
	
	.control-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 10px 10px;
		border: none;
		border-radius: 50%;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		color: #9ca3af;
	}
	
	.control-btn:hover {
		background: #4b5563;
		color: #f9fafb;
	}

	.mic-btn{
		padding: 5px 5px;
	}
	
	.control-btn.active {
		background: #10b981;
		color: white;
	}
	
	.end-btn {
		background: #ef4444 !important;
		color: white !important;
	}
	
	.end-btn:hover {
		background: #dc2626 !important;
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
	
	@media (max-width: 768px) {
		.video-grid {
			grid-template-columns: 1fr;
		}
		
		.meeting-controls {
			flex-wrap: wrap;
		}
		
		.control-btn {
			flex: 1;
			min-width: 120px;
		}
	}
</style>