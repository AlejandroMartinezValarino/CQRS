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

export const SEARCH_ANIMES = gql`
  query SearchAnimes($page: Int!, $pageSize: Int!, $filters: AnimeFilters) {
    searchAnimes(page: $page, pageSize: $pageSize, filters: $filters) {
      items {
        myanimelistId
        title
        description
        image
        type
        episodes
        score
        popularity
        genres
        totalClicks
        totalViews
        totalRatings
        averageRating
      }
      total
      page
      pageSize
      hasMore
    }
  }
`;

export const TRENDING_ANIMES = gql`
  query TrendingAnimes($limit: Int!, $days: Int) {
    trendingAnimes(limit: $limit, days: $days) {
      myanimelistId
      title
      description
      image
      type
      episodes
      score
      popularity
      genres
      totalClicks
      totalViews
      totalRatings
      averageRating
    }
  }
`;

export const RECOMMENDED_ANIMES = gql`
  query RecommendedAnimes($basedOnAnimeId: Int!, $limit: Int!) {
    recommendedAnimes(basedOnAnimeId: $basedOnAnimeId, limit: $limit) {
      myanimelistId
      title
      description
      image
      type
      episodes
      score
      popularity
      genres
      totalClicks
      totalViews
      totalRatings
      averageRating
    }
  }
`;

export const GENRES = gql`
  query Genres {
    genres
  }
`;
