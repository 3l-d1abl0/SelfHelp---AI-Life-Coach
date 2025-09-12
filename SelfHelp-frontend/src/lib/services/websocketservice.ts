import { PUBLIC_BACKEND_SERVER_URL, PUBLIC_ASSEMBLYAI_WEBSOCKET_URL } from '$env/static/public';

type handleTranscription = (x: string, y: boolean) => void;
type handleError = (err: Event | Error) => void;
type handleConnect = () => void;
type handleAIMentorMessage = (message: string) => void;
type handleInitiation = (initMessage: string) => void;

export class WebSocketService {
    
    ws: WebSocket | null;
    onError: handleError | null;
    onConnect: handleConnect | null;
    onAIMentorMessage: handleAIMentorMessage | null;
    meetingId: string;
    onInitiation: handleInitiation| null;

    constructor(meetingId: string) {
        this.ws = null;
        this.onError = null;
        this.onConnect = null;
        this.onAIMentorMessage = null;
        this.meetingId = meetingId;
        this.onInitiation = null;

        if (!this.meetingId) {
            console.error('Missing meeting id');
        }
    }
  

  connect(){


    return new Promise((resolve, reject)=>{
      try{

        const self = this;
        const endpoint = `${PUBLIC_BACKEND_SERVER_URL}/ws/${this.meetingId}`

        this.ws = new WebSocket(endpoint);
  
        this.ws.onopen = function(event) {
            console.log('CONNECTION ESTABLISHED: ');
            console.log(event);

            if (self.onConnect) self.onConnect();

            console.log('resolving...');
            resolve('CONNECTED');
        };
        
        this.ws.onmessage = function(event) {
          console.log("RECIEVED:");

          let data = JSON.parse(event.data)
            console.log(data.type);
            if(data.type == "conversation"){

              console.log("conversation ... ");
              if(self.onAIMentorMessage)
                self.onAIMentorMessage(data.message);
              
            }else if (data.type == "initiation"){

              console.log('Initalized !!!');
              if(self.onInitiation)
                self.onInitiation(data.message);
            }
        };
        
        this.ws.onclose = function(event) {
            
            console.log('CLOSED: ');
            if (event.wasClean) {
              console.log('CLEAN');
            } else {
                console.log('Connection died');
                reject();
            }
            console.log(event);
        };
        
        this.ws.onerror = function(error) {
            console.log('CONNECTION ERROR: ');
            console.log(error);
            reject(error);
        };
  
      }catch(error){
        console.log(error);
        //reject();
      }

    });

  }


  askMentor(data: string) {

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        
        console.log('asking mentor via websocket .... ');

      try {
          let user_message = {
            "type": "user_message",
            "message" : data
          };

          this.ws.send(JSON.stringify(user_message));
          console.log('SENT DATA: ', user_message);

      } catch (error) {
          console.log('ERROR WHILE SENDING ... : ');
          console.log(error);
      }

    }

  }//askMentor


  terminate() {
    if (this.ws) {
      this.ws.send(JSON.stringify({ type: 'terminate' }));
      this.ws.close();
      this.ws = null;
    }
  }
}