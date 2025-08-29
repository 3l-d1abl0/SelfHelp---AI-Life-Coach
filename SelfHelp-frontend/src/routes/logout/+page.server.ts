import { signOut } from '$lib/server/auth.js';
import { redirect } from '@sveltejs/kit';
import logger from '$lib/server/logger.js';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const session = await event.locals.auth();
    console.log('Session before logout ...');
	
	if (session?.user) {
		logger.info(`User logged out: ${session.user.email}`);
		//await signOut(event);
		//await event.locals.auth().signOut();

		console.log('After sign out  ...');
	}else{
		logger.info(`No user Found !!!`);
		throw redirect(302, '/');
	}
	

	return {};
};

export const actions: Actions = {
    default: async (event) => {
        const session = await event.locals.auth();
        if (session?.user) {
            logger.info(`logging out ....: ${session.user.email}`);
            await signOut(event);
			logger.warn('REDIRECTING ......');
			throw redirect(303, '/');
        }
    }
};