// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		interface Error {
			message: string;
			code?: string;
		  }
		  
		  interface Locals {
			auth(): Promise<Session | null>;
			user?: {
			  id: string;
			  name?: string | null;
			  email?: string | null;
			  image?: string | null;
			} | null;
		  }
		  
		  interface PageData {
			session?: Session | null;
		  }
		  
		  interface PageState {}
		  
		  interface Platform {}
		}
}

export {};
