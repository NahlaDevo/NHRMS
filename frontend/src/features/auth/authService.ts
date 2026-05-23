import { api } from '@/lib/axios';
import type { LoginRequest, LoginResponse, User } from '@/types';

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });
  failedQueue = [];
}

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const res = await api.post<LoginResponse>('/auth/login', data);
    return res.data;
  },

  async getMe(token: string): Promise<User> {
    const res = await api.get<User>('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const res = await api.post<LoginResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return res.data;
  },

  setupInterceptor() {
    api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            }).then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return api(originalRequest);
            });
          }

          originalRequest._retry = true;
          isRefreshing = true;

          try {
            const storedRefresh = localStorage.getItem('refresh_token');
            if (!storedRefresh) throw new Error('No refresh token');

            const res = await authService.refreshToken(storedRefresh);
            const newToken = res.access_token;

            localStorage.setItem('access_token', newToken);
            if (res.refresh_token) {
              localStorage.setItem('refresh_token', res.refresh_token);
            }

            processQueue(null, newToken);
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          } catch (refreshError) {
            processQueue(refreshError, null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  },
};
