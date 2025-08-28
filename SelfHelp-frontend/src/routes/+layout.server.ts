import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async (event) => {
	const session = await event.locals.auth();
	console.log('LAYOUT SERVER : Session before Layout !!!');
	console.log(session);
	return {
		session
	};
};