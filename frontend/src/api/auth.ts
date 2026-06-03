import apiClient from './client';

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface UserInfo {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  created_at: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export const login = (data: LoginData) => {
  return apiClient.post<unknown, AuthResponse>('/api/v1/auth/login', data);
};

export const register = (data: RegisterData) => {
  return apiClient.post<unknown, AuthResponse>('/api/v1/auth/register', data);
};
