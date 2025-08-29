import { redirect } from '@sveltejs/kit';
import logger from '$lib/server/logger.js';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {

    //logger.info('REFERRER: ',event.request.headers.get('referer'));
	let referer = event.request.headers.get('referer');
	referer = referer == null ? '/meeting/new': referer

	const session = await event.locals.auth();
	
	if (session?.user) {
		logger.warn(`Logged in ${session.user.email}`);
		redirect(302, referer);
	}
	
	return {
		referer: referer
	};
};