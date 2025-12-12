import { gql } from '@apollo/client';

export const TOP_ANIMES_BY_VIEWS = gql`
  query TopAnimesByViews($limit: Int!) {
    topAnimesByViews(limit: $limit) {
      animeId
      totalClicks
      totalViews
      totalRatings
      averageRating
      totalDurationSeconds
    }
  }
`;

export const TOP_ANIMES_BY_RATING = gql`
  query TopAnimesByRating($limit: Int!) {
    topAnimesByRating(limit: $limit) {
      animeId
      totalClicks
      totalViews
      totalRatings
      averageRating
      totalDurationSeconds
    }
  }
`;

export const ANIME_STATS = gql`
  query AnimeStats($animeId: Int!) {
    animeStats(animeId: $animeId) {
      animeId
      totalClicks
      totalViews
      totalRatings
      averageRating
      totalDurationSeconds
    }
  }
`;

export const ANIME = gql`
  query Anime($animeId: Int!) {
    anime(animeId: $animeId) {
      myanimelistId
      title
      description
      image
      type
      episodes
      score
      popularity
    }
  }
`;
