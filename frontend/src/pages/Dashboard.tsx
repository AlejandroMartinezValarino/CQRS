import { Row, Col, Card, Statistic, Table } from 'antd';
import { EyeOutlined, LikeOutlined, StarOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useTopAnimesByViews, useTopAnimesByRating } from '@/hooks/useGraphQL';
import { Loading } from '@/components/common/Loading';
import { formatNumber, formatDuration } from '@/utils';

const columns = [
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
  const { data: viewsData, loading: viewsLoading } = useTopAnimesByViews(10);
  const { data: ratingData, loading: ratingLoading } = useTopAnimesByRating(10);

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

  return (
    <div style={{ padding: '24px' }}>
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
