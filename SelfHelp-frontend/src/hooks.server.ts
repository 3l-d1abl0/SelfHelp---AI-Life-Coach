import { handle as authHandle } from '$lib/server/auth';
import { isRedirect, redirect, type Handle } from '@sveltejs/kit';
import logger from '$lib/server/logger.js';

const protectedRoutes = ['/profile', '/meeting', '/logout'];

// This is a workaround for the cookie setting issue
export const handle: Handle = async ({ event, resolve }) => {
    // Log every request
    logger.info(`${event.request.method} ${event.url.pathname} - ${event.getClientAddress()}`);
    
    // Skip session handling for static assets and API routes
    if (event.url.pathname.startsWith('/_app/') || event.url.pathname.startsWith('/api/')) {
        return await resolve(event);
    }
    
    // Get the session once at the beginning
    let session = null;
    try {


        session = await event.locals.auth?.();
        
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
        if (protectedRoutes.some(route => event.url.pathname.startsWith(route))) {
            if (!session?.user) {
                logger.warn(`Unauthorized access : ${event.url}`);
                redirect(302, '/login');
            }
        }
        
    } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.log("_________");
        console.log(error);
        logger.error(`Error in session handling: ${errorMessage}`);
        // if (error instanceof Error && 'status' in error) {
        //     // If it's a redirect, rethrow it
        //     logger.error('throwing ...');
        //     throw error;
        // }

        if(isRedirect(error))
            throw error;
        // For other errors, we'll let the request continue but log the error
    }
    
    // Handle the request with auth
    return authHandle({ event, resolve });
};