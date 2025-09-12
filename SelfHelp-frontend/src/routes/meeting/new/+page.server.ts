import { redirect } from '@sveltejs/kit';
import logger from '$lib/server/logger.js';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {

	console.log('REFERRER: ',event.request.headers.get('referer'));
	const session = await event.locals.auth();
	
	// if (!session?.user) {
	// 	logger.warn('Unauthorized profile access attempt');
	// 	redirect(302, '/login');
	// }
	
	logger.info(`Profile page loaded for user: ${session.user.email}`);
		
	
	return {
		user: session.user
	};
};