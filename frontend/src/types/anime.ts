export interface Anime {
  myanimelistId: number;
  title: string;
  description?: string | null;
  image?: string | null;
  type?: string | null;
  episodes?: number | null;
  score?: number | null;
  popularity?: number | null;
}

export interface AnimeStats {
  animeId: number;
  totalClicks: number;
  totalViews: number;
  totalRatings: number;
  averageRating?: number | null;
  totalDurationSeconds: number;
}

export interface TopAnime extends AnimeStats {
  anime?: Anime | null;
}

export interface AnimeWithStats {
  myanimelistId: number;
  title: string;
  description?: string | null;
  image?: string | null;
  type?: string | null;
  episodes?: number | null;
  score?: number | null;
  popularity?: number | null;
  genres?: string | null;
  totalClicks: number;
  totalViews: number;
  totalRatings: number;
  averageRating?: number | null;
}

export interface PaginatedAnimes {
  items: AnimeWithStats[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface AnimeFilters {
  search?: string;
  type?: string;
  genres?: string[];
  minScore?: number;
  sortBy?: 'popularity' | 'score' | 'title' | 'views';
}
