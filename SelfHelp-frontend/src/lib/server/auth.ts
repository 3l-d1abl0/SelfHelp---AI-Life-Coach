import { SvelteKitAuth } from '@auth/sveltekit';
import Google from '@auth/sveltekit/providers/google';
import { MongoDBAdapter } from '@auth/mongodb-adapter';
import { MongoClient } from 'mongodb';
import { GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, AUTH_SECRET, MONGODB_URI } from '$env/static/private';
import logger from './logger';
import type { Account, Profile, User } from '@auth/core/types';

const client = new MongoClient(MONGODB_URI);

export const { handle, signIn, signOut } = SvelteKitAuth({
	adapter: MongoDBAdapter(client),
	providers: [
		Google({
			clientId: GOOGLE_CLIENT_ID,
			clientSecret: GOOGLE_CLIENT_SECRET
		})
	],
	secret: AUTH_SECRET,
	trustHost: true,
	callbacks: {
		async signIn({ user, account, profile }: { user: User; account: Account | null; profile?: Profile }) {
			logger.info(`User signed in: ${user.email} via ${account?.provider}`);
			return true;
		},
		async session({ session, token }) {
			logger.info(`Session accessed for user: ${session.user?.email}`);
			return session;
		},
		async jwt({ token, user }) {
			if (user) {
				token.sub = user.id;
			}
			return token;
		}
	},
	pages: {
		signIn: '/login',
		error: '/error'
	}
});