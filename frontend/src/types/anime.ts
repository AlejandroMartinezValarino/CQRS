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
