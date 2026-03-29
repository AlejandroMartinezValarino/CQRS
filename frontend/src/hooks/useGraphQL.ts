import { useQuery } from '@apollo/client';
import { TOP_ANIMES_BY_VIEWS, TOP_ANIMES_BY_RATING, ANIME_STATS, ANIME } from '@/services/graphql/queries';
import type { AnimeStats, Anime } from '@/types/anime';

/** El read model se actualiza vía Kafka; no usar solo caché o verás cifras viejas al volver al dashboard. */
const READ_MODEL_FETCH = 'cache-and-network' as const;

export const useTopAnimesByViews = (limit: number = 10) => {
  return useQuery<{ topAnimesByViews: AnimeStats[] }>(TOP_ANIMES_BY_VIEWS, {
    variables: { limit },
    fetchPolicy: READ_MODEL_FETCH,
  });
};

export const useTopAnimesByRating = (limit: number = 10) => {
  return useQuery<{ topAnimesByRating: AnimeStats[] }>(TOP_ANIMES_BY_RATING, {
    variables: { limit },
    fetchPolicy: READ_MODEL_FETCH,
  });
};

export const useAnimeStats = (animeId: number) => {
  return useQuery<{ animeStats: AnimeStats | null }>(ANIME_STATS, {
    variables: { animeId },
    skip: !animeId || animeId <= 0,
    fetchPolicy: READ_MODEL_FETCH,
  });
};

export const useAnime = (animeId: number) => {
  return useQuery<{ anime: Anime | null }>(ANIME, {
    variables: { animeId },
    skip: !animeId || animeId <= 0,
  });
};
