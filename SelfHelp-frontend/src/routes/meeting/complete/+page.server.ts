import type { PageServerLoad } from './$types';


export const load: PageServerLoad = async (event) => {

	console.log('REFERRER: ',event.request.headers.get('referer'));
	const session = await event.locals.auth();

	return {
		user: session.user
	};
};