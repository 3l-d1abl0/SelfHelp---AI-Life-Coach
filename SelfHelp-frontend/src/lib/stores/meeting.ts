import { writable, type Writable } from 'svelte/store';



export const transcription = writable('');
export const isRecording = writable(false);
export const assemblyWs = writable(null);
export const mediaStream: Writable<MediaStream | null> = writable(null);
export const cameraEnabled = writable(true);
export const micEnabled = writable(true);
export const meetingId = writable(null);
export const meetingStatus = writable('idle'); // idle, connecting, ready, active, ended
export const errorMessage = writable('');
export const successMessage = writable('');