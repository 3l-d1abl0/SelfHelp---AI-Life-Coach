import type { ObjectId, WithId, Document } from 'mongodb';

// Base User interface for database operations
export interface User extends WithId<Document> {
  _id: ObjectId;
  name: string;
  email: string;
  image: string;
  emailVerified?: Date;
}

// Serialized User interface for client-side use
export interface SerializedUser {
  _id: string;
  name: string;
  email: string;
  image: string;
  emailVerified?: string;
}

export interface PaginationData {
  currentPage: number;
  totalPages: number;
  totalUsers: number;
}

export interface UserListData {
  users: SerializedUser[];
  pagination: PaginationData;
}

export interface AuthError {
  error: string;
  description?: string;
}

// Helper function to convert a User to a SerializedUser
export function serializeUser(user: User): SerializedUser {
  return {
    _id: user._id.toString(),
    name: user.name,
    email: user.email,
    image: user.image,
    emailVerified: user.emailVerified?.toISOString()
  };
}