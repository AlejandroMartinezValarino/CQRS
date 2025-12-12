export interface ClickCommand {
  anime_id: number;
  user_id: string;
}

export interface ViewCommand {
  anime_id: number;
  user_id: string;
  duration_seconds: number;
}

export interface RatingCommand {
  anime_id: number;
  user_id: string;
  rating: number;
}

export interface ApiResponse {
  status: string;
  message: string;
}
