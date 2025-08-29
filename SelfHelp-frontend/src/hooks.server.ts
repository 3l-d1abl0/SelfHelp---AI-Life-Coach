import { handle as authHandle } from '$lib/server/auth';
import { isRedirect, redirect, type Handle } from '@sveltejs/kit';
import logger from '$lib/server/logger.js';
import { sequence } from '@sveltejs/kit/hooks';

const protectedRoutes = ['/profile', '/meeting', '/logout'];

// First, handle authentication
export const handleAuth = authHandle;

// Then, handle our custom logic
export const handleSession: Handle = async ({ event, resolve }) => {

    logger.error("__________________________________________");
    // Skip session handling for static assets and API routes
    if (event.url.pathname.startsWith('/_app/') || event.url.pathname.startsWith('/api/')) {
        return await resolve(event);
    }

    try {
        // Get the session
        const session = await event.locals.auth?.();
        logger.info(`HOOKS: Session for ${event.url.pathname}: ${JSON.stringify(session)}`);

        // Set user in locals if available
        if (session?.user) {
            event.locals.user = {
                id: session.user.id || '',
                name: session.user.name || null,
                email: session.user.email || null,
                image: session.user.image || null
            };
        } else {
            event.locals.user = null;
        }

        // Check protected routes
        if (protectedRoutes.some(route => event.url.pathname.startsWith(route)) && !session?.user) {
            logger.warn(`Unauthorized access attempt to ${event.url.pathname}`);
            throw redirect(303, '/login');
        }

        return await resolve(event);
    } catch (error) {
        logger.error(`Error in handleSession: ${error}`);
        throw error;
    }
};

// Chain the handlers
export const handle = sequence(handleAuth, handleSession);