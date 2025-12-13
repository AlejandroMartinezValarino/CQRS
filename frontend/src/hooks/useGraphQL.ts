import { useQuery } from '@apollo/client';
import {
  TOP_ANIMES_BY_VIEWS,
  TOP_ANIMES_BY_RATING,
  ANIME_STATS,
  ANIME,
  SEARCH_ANIMES,
  TRENDING_ANIMES,
  RECOMMENDED_ANIMES,
  GENRES,
} from '@/services/graphql/queries';
import type {
  AnimeStats,
  Anime,
  PaginatedAnimes,
  AnimeWithStats,
  AnimeFilters,
} from '@/types/anime';

export const useTopAnimesByViews = (limit: number = 10) => {
  return useQuery<{ topAnimesByViews: AnimeStats[] }>(TOP_ANIMES_BY_VIEWS, {
    variables: { limit },
  });
};

export const useTopAnimesByRating = (limit: number = 10) => {
  return useQuery<{ topAnimesByRating: AnimeStats[] }>(TOP_ANIMES_BY_RATING, {
    variables: { limit },
  });
};

export const useAnimeStats = (animeId: number) => {
  return useQuery<{ animeStats: AnimeStats | null }>(ANIME_STATS, {
    variables: { animeId },
    skip: !animeId || animeId <= 0,
  });
};

export const useAnime = (animeId: number) => {
  return useQuery<{ anime: Anime | null }>(ANIME, {
    variables: { animeId },
    skip: !animeId || animeId <= 0,
  });
};

export const useSearchAnimes = (
  page: number,
  pageSize: number,
  filters?: AnimeFilters
) => {
  return useQuery<{ searchAnimes: PaginatedAnimes }>(SEARCH_ANIMES, {
    variables: { page, pageSize, filters },
    fetchPolicy: 'cache-and-network',
  });
};

export const useTrendingAnimes = (limit: number = 10, days: number = 7) => {
  return useQuery<{ trendingAnimes: AnimeWithStats[] }>(TRENDING_ANIMES, {
    variables: { limit, days },
    pollInterval: 60000,
  });
};

export const useRecommendedAnimes = (basedOnAnimeId: number, limit: number = 10) => {
  return useQuery<{ recommendedAnimes: AnimeWithStats[] }>(RECOMMENDED_ANIMES, {
    variables: { basedOnAnimeId, limit },
    skip: !basedOnAnimeId || basedOnAnimeId <= 0,
  });
};

export const useGenres = () => {
  return useQuery<{ genres: string[] }>(GENRES);
};
