import { PUBLIC_BACKEND_SERVER_URL, PUBLIC_ASSEMBLYAI_WEBSOCKET_URL } from '$env/static/public';


type handleTranscription = (x: string, y: boolean) => void;
type handleAssemblyError = (err: Event | Error) => void;
type handleAssemblyConnect = () => void;

export class AssemblyAIService {

  ws: WebSocket | null;
  onTranscription: handleTranscription | null;
  onError: handleAssemblyError | null;
  onConnect: handleAssemblyConnect | null;
  
  constructor() {
    this.ws = null;
    this.onTranscription = null;
    this.onError = null;
    this.onConnect = null;
  }
  
  connect() {


    return new Promise((resolve, reject)=>{
      
      //Get the temp streaming Key
      fetch(`${PUBLIC_BACKEND_SERVER_URL}/api/v1/assemblyaiToken`, {
        method: 'POST',
				headers: {
          'Content-Type': 'application/json'
				}
			}).then(async response =>{
        
        const authData = await response.json();
        if (!response.ok){
          
          console.log(authData.detail);
          //throw new Error(authData.detail || 'Failed to streaming Token');
          reject(authData.detail);
        }
        
        return authData.token;
        
      }).then( authToken => {
        
        //console.log('AUTH KEY: ', authToken);
        const CONNECTION_PARAMS : { token: string, sample_rate: number, format_turns: boolean } = {
          token: authToken,
          sample_rate: 16000,
          format_turns: true,
        };

        const params = new URLSearchParams(CONNECTION_PARAMS);
        const endpoint = `${PUBLIC_ASSEMBLYAI_WEBSOCKET_URL}?${params.toString()}`;
        

        //Connect to AsemblyAI Websocket for transcription
        this.ws = new WebSocket(endpoint);

        //Handle the message event from Websocket
        this.ws.addEventListener('message', (event) => {

          try {

              const data = JSON.parse(event.data);
              //console.log('EventData: ', data.type);
              const msgType = data.type;

              if (msgType === "Begin") {//Connected Successfully
                
                console.log(`Trascription Session began: ID=${data.id}`);
                  if (this.onConnect)
                    this.onConnect();

                  resolve();

              } else if (msgType === "Turn") {//Handle the incoming transcription
                
                const transcript = data.transcript || "";
                const formatted = data.turn_is_formatted;
                
                //console.log('DATA: ', data);
                //console.log('TRANSCRIPT DATA: ', transcript);
                if (this.onTranscription) {
                  this.onTranscription(transcript, formatted);
                }

              } else if (msgType === "Termination") {//handle the Session termination event
                console.log(`Session terminated`);
              }

          } catch (error: Error) {
            console.error('Error handling message:', error);
            if (this.onError) this.onError(error);
          }

        });

        //hadle error events from Websocket
        this.ws.addEventListener('error', (error: Event) => {
          console.error('WebSocket Error:', error);
          if (this.onError) this.onError(error);
          reject(error);
        });

        //handle the close Event from Websocket
        this.ws.addEventListener('close', (event) => {
          console.log(`WebSocket Disconnected: Status=${event.code}`);
          console.log(event.reason)
        });
    });


    });

  }

  sendAudio(audioData) {
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      //console.log('Sent audio .... ');
      this.ws.send(audioData);
    }

  }

  terminate() {
    if (this.ws) {
      this.ws.send(JSON.stringify({ type: 'terminate' }));
      this.ws.close();
      this.ws = null;
    }
  }
}