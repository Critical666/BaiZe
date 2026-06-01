import apiClient from './client';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: { id: string; username: string; email: string; role: string; created_at: string };
}

export const login = (data: LoginData) => {
  return apiClient.post<unknown, AuthResponse>('/api/v1/auth/login', data);
};

export const register = (data: RegisterData) => {
  return apiClient.post<unknown, AuthResponse>('/api/v1/auth/register', data);
};
