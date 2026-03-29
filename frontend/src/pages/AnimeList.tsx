import { useState } from 'react';
import { Card, Input, Row, Col, Empty } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTopAnimesByViews } from '@/hooks/useGraphQL';
import { Loading } from '@/components/common/Loading';
import type { AnimeStats } from '@/types/anime';

const { Search } = Input;

export const AnimeList = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const { data, loading } = useTopAnimesByViews(100);

  const filteredData =
    data?.topAnimesByViews.filter((anime: AnimeStats) => {
      const q = searchTerm.trim().toLowerCase();
      if (!q) return true;
      if (anime.animeId.toString().includes(searchTerm.trim())) return true;
      if (anime.title?.toLowerCase().includes(q)) return true;
      return false;
    }) || [];

  if (loading) {
    return <Loading />;
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Search
          placeholder="Buscar por ID o título"
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          onSearch={setSearchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ maxWidth: '400px' }}
        />
      </div>

      {filteredData.length === 0 ? (
        <Empty description="No se encontraron animes" />
      ) : (
        <Row gutter={[16, 16]}>
          {filteredData.map((anime: AnimeStats) => (
            <Col xs={24} sm={12} md={8} lg={6} key={anime.animeId}>
              <Card
                hoverable
                onClick={() => navigate(`/animes/${anime.animeId}`)}
                style={{ height: '100%' }}
                cover={
                  anime.image ? (
                    <img
                      alt=""
                      src={anime.image}
                      style={{ height: 220, objectFit: 'cover' }}
                    />
                  ) : undefined
                }
              >
                <div style={{ textAlign: 'center' }}>
                  <h3 style={{ marginTop: 0 }}>
                    {anime.title?.trim() || `Anime #${anime.animeId}`}
                  </h3>
                  <p style={{ color: '#888', fontSize: 12 }}>#{anime.animeId}</p>
                  <p><strong>Clicks:</strong> {anime.totalClicks}</p>
                  <p><strong>Views:</strong> {anime.totalViews}</p>
                  <p><strong>Ratings:</strong> {anime.totalRatings}</p>
                  {anime.averageRating && (
                    <p><strong>Rating:</strong> {anime.averageRating.toFixed(2)}</p>
                  )}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};
