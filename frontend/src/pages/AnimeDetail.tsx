import { useParams, useNavigate } from 'react-router-dom';
import { Card, Row, Col, Statistic, Button, Empty } from 'antd';
import { ArrowLeftOutlined, EyeOutlined, LikeOutlined, StarOutlined } from '@ant-design/icons';
import { useAnime, useAnimeStats } from '@/hooks/useGraphQL';
import { useAnimeVisitTracking } from '@/hooks/useAnimeVisitTracking';
import { Loading } from '@/components/common/Loading';
import { formatNumber, formatDuration } from '@/utils';

export const AnimeDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const animeId = id ? parseInt(id, 10) : 0;

  const { data: animeData, loading: animeLoading } = useAnime(animeId);
  const { data: statsData, loading: statsLoading } = useAnimeStats(animeId);

  const anime = animeData?.anime;
  const stats = statsData?.animeStats;
  // No exigir !statsLoading si ya tenemos `anime`: al refetchear tras el click, statsLoading
  // puede volver a true, el efecto de tracking hacía cleanup y reiniciaba el cronómetro (duración ~0).
  const canTrackVisit =
    !animeLoading &&
    (!!anime || (!!stats && !statsLoading));

  useAnimeVisitTracking(animeId, canTrackVisit);

  if (animeLoading || statsLoading) {
    return <Loading />;
  }

  if (!anime && !stats) {
    return (
      <div style={{ padding: '24px' }}>
        <Empty description="Anime no encontrado" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/animes')}
        style={{ marginBottom: '16px' }}
      >
        Volver
      </Button>

      {anime && (
        <Card title={anime.title} style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]}>
            {anime.image && (
              <Col xs={24} md={8}>
                <img
                  src={anime.image}
                  alt={anime.title}
                  style={{ width: '100%', borderRadius: '8px' }}
                />
              </Col>
            )}
            <Col xs={24} md={anime.image ? 16 : 24}>
              {anime.description && (
                <p style={{ marginBottom: '16px' }}>{anime.description}</p>
              )}
              <Row gutter={16}>
                {anime.type && (
                  <Col span={12}>
                    <p><strong>Tipo:</strong> {anime.type}</p>
                  </Col>
                )}
                {anime.episodes && (
                  <Col span={12}>
                    <p><strong>Episodios:</strong> {anime.episodes}</p>
                  </Col>
                )}
                {anime.score && (
                  <Col span={12}>
                    <p><strong>Score:</strong> {anime.score}</p>
                  </Col>
                )}
                {anime.popularity && (
                  <Col span={12}>
                    <p><strong>Popularidad:</strong> {formatNumber(anime.popularity)}</p>
                  </Col>
                )}
              </Row>
            </Col>
          </Row>
        </Card>
      )}

      {stats && (
        <Card title="Estadísticas">
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="Total Clicks"
                value={stats.totalClicks}
                prefix={<LikeOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="Total Visualizaciones"
                value={stats.totalViews}
                prefix={<EyeOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="Total Calificaciones"
                value={stats.totalRatings}
                prefix={<StarOutlined />}
                valueStyle={{ color: '#cf1322' }}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic
                title="Rating Promedio"
                value={stats.averageRating ? stats.averageRating.toFixed(2) : 'N/A'}
                prefix={<StarOutlined />}
              />
            </Col>
            <Col xs={24}>
              <Statistic
                title="Duración Total"
                value={formatDuration(stats.totalDurationSeconds)}
              />
            </Col>
          </Row>
        </Card>
      )}

      <Card style={{ marginTop: '24px' }} title="Interacciones manuales">
        <p style={{ marginBottom: 12, color: '#666' }}>
          El click y el tiempo en esta ficha se registran solos. Aquí puedes enviar otra vista,
          un click extra o una calificación.
        </p>
        <Button
          type="primary"
          onClick={() => navigate(`/interactions?anime_id=${animeId}`)}
          style={{ marginRight: '8px' }}
        >
          Abrir formulario
        </Button>
      </Card>
    </div>
  );
};
