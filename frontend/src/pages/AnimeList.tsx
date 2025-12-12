import { useState } from 'react';
import { Card, Input, Row, Col, Spin, Empty } from 'antd';
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

  const filteredData = data?.topAnimesByViews.filter((anime: AnimeStats) =>
    anime.animeId.toString().includes(searchTerm)
  ) || [];

  if (loading) {
    return <Loading />;
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Search
          placeholder="Buscar por Anime ID"
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
              >
                <div style={{ textAlign: 'center' }}>
                  <h3>Anime #{anime.animeId}</h3>
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
