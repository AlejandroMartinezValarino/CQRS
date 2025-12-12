import { useQuery } from '@apollo/client';
import { TOP_ANIMES_BY_VIEWS, TOP_ANIMES_BY_RATING, ANIME_STATS, ANIME } from '@/services/graphql/queries';
import type { AnimeStats, Anime } from '@/types/anime';

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
