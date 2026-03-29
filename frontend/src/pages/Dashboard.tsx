import { Row, Col, Card, Statistic, Table, Alert } from 'antd';
import { EyeOutlined, LikeOutlined, StarOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useTopAnimesByViews, useTopAnimesByRating } from '@/hooks/useGraphQL';
import { Loading } from '@/components/common/Loading';
import { formatNumber, formatDuration } from '@/utils';
const columns = [
  {
    title: '',
    dataIndex: 'image',
    key: 'image',
    width: 64,
    render: (url: string | null | undefined) =>
      url ? (
        <img
          src={url}
          alt=""
          style={{ width: 48, height: 64, objectFit: 'cover', borderRadius: 4 }}
        />
      ) : (
        <span style={{ color: '#999' }}>—</span>
      ),
  },
  {
    title: 'Título',
    dataIndex: 'title',
    key: 'title',
    ellipsis: true,
    render: (t: string | null | undefined, record: { animeId: number }) =>
      t?.trim() || `Anime #${record.animeId}`,
  },
  {
    title: 'Anime ID',
    dataIndex: 'animeId',
    key: 'animeId',
  },
  {
    title: 'Clicks',
    dataIndex: 'totalClicks',
    key: 'totalClicks',
    render: (value: number) => formatNumber(value),
  },
  {
    title: 'Visualizaciones',
    dataIndex: 'totalViews',
    key: 'totalViews',
    render: (value: number) => formatNumber(value),
  },
  {
    title: 'Calificaciones',
    dataIndex: 'totalRatings',
    key: 'totalRatings',
    render: (value: number) => formatNumber(value),
  },
  {
    title: 'Rating Promedio',
    dataIndex: 'averageRating',
    key: 'averageRating',
    render: (value: number | null) => value ? value.toFixed(2) : 'N/A',
  },
  {
    title: 'Duración Total',
    dataIndex: 'totalDurationSeconds',
    key: 'totalDurationSeconds',
    render: (value: number) => formatDuration(value),
  },
];

export const Dashboard = () => {
  const { data: viewsData, loading: viewsLoading, error: viewsError } = useTopAnimesByViews(10);
  const { data: ratingData, loading: ratingLoading, error: ratingError } = useTopAnimesByRating(10);

  const totalStats = viewsData?.topAnimesByViews.reduce(
    (acc, curr) => ({
      clicks: acc.clicks + curr.totalClicks,
      views: acc.views + curr.totalViews,
      ratings: acc.ratings + curr.totalRatings,
      duration: acc.duration + curr.totalDurationSeconds,
    }),
    { clicks: 0, views: 0, ratings: 0, duration: 0 }
  ) || { clicks: 0, views: 0, ratings: 0, duration: 0 };

  if (viewsLoading || ratingLoading) {
    return <Loading />;
  }

  if (viewsError || ratingError) {
    const msg = [viewsError?.message, ratingError?.message]
      .filter((m): m is string => Boolean(m))
      .join(' · ');
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          type="error"
          showIcon
          message="No se pudo cargar el dashboard desde GraphQL"
          description={
            <>
              <p>{msg}</p>
              <p style={{ marginBottom: 0 }}>
                Comprueba que el read-side responda (p. ej. <code>POST /graphql</code> vía el mismo origen
                que la web), Nginx y CORS. En consola del navegador suele aparecer el detalle (502, red,
                bloqueo).
              </p>
            </>
          }
        />
      </div>
    );
  }

  const viewsRows = viewsData?.topAnimesByViews ?? [];
  const hasNoViewStats = viewsRows.length === 0;

  return (
    <div style={{ padding: '24px' }}>
      {hasNoViewStats && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message="Aún no hay ranking por visualizaciones"
          description={
            'Solo se listan animes con total_views > 0. Ejecuta el seed de estadísticas o genera visitas; ' +
            'las actualizaciones del consumer pueden tardar unos segundos.'
          }
        />
      )}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Clicks"
              value={totalStats.clicks}
              prefix={<LikeOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Visualizaciones"
              value={totalStats.views}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Calificaciones"
              value={totalStats.ratings}
              prefix={<StarOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Duración Total"
              value={formatDuration(totalStats.duration)}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Top 10 Animes por Visualizaciones">
            <Table
              dataSource={viewsData?.topAnimesByViews || []}
              columns={columns}
              rowKey="animeId"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Top 10 Animes por Rating">
            <Table
              dataSource={ratingData?.topAnimesByRating || []}
              columns={columns}
              rowKey="animeId"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
