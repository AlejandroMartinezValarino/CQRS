import axios from 'axios';
import type { ClickCommand, ViewCommand, RatingCommand, ApiResponse } from '@/types/commands';

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const commandService = {
  async registerClick(command: ClickCommand): Promise<ApiResponse> {
    const response = await apiClient.post<ApiResponse>('/click', command);
    return response.data;
  },

  async registerView(command: ViewCommand): Promise<ApiResponse> {
    const response = await apiClient.post<ApiResponse>('/view', command);
    return response.data;
  },

  async registerRating(command: RatingCommand): Promise<ApiResponse> {
    const response = await apiClient.post<ApiResponse>('/rating', command);
    return response.data;
  },
};
