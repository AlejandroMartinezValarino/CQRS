import { Card, Carousel, Row, Col, Typography, Space, Tag } from 'antd';
import { FireOutlined, EyeOutlined, StarOutlined } from '@ant-design/icons';
import { useTrendingAnimes } from '@/hooks/useGraphQL';
import { useNavigate } from 'react-router-dom';
import { formatNumber } from '@/utils';

const { Title, Text, Paragraph } = Typography;

export const TrendingSection = () => {
  const { data, loading } = useTrendingAnimes(10);
  const navigate = useNavigate();

  if (loading || !data?.trendingAnimes?.length) {
    return null;
  }

  return (
    <Card
      title={
        <Space>
          <FireOutlined style={{ color: '#ff4d4f' }} />
          <Title level={4} style={{ margin: 0 }}>
            Trending Ahora
          </Title>
        </Space>
      }
      style={{ marginBottom: 24 }}
    >
      <Carousel autoplay autoplaySpeed={5000} dots={{ className: 'custom-dots' }}>
        {data.trendingAnimes.map((anime) => (
          <div key={anime.myanimelistId}>
            <div
              onClick={() => navigate(`/animes/${anime.myanimelistId}`)}
              style={{
                cursor: 'pointer',
                position: 'relative',
                height: 400,
                borderRadius: 8,
                overflow: 'hidden',
                backgroundImage: `url(${anime.image || '/placeholder-anime.jpg'})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(to right, rgba(0,0,0,0.9) 30%, transparent 70%)',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0 48px',
                }}
              >
                <Row style={{ maxWidth: 600 }}>
                  <Col span={24}>
                    <Space direction="vertical" size="middle">
                      <div>
                        {anime.type && <Tag color="blue">{anime.type}</Tag>}
                        {anime.score && (
                          <Tag color="gold" icon={<StarOutlined />}>
                            {anime.score.toFixed(1)}
                          </Tag>
                        )}
                      </div>
                      <Title level={2} style={{ color: 'white', margin: 0 }}>
                        {anime.title}
                      </Title>
                      {anime.description && (
                        <Paragraph
                          ellipsis={{ rows: 3 }}
                          style={{ color: 'rgba(255,255,255,0.8)', marginBottom: 0 }}
                        >
                          {anime.description}
                        </Paragraph>
                      )}
                      <Space size="large">
                        <Space>
                          <EyeOutlined style={{ color: 'white' }} />
                          <Text style={{ color: 'white' }}>
                            {formatNumber(anime.totalViews)} views
                          </Text>
                        </Space>
                        {anime.episodes && (
                          <Text style={{ color: 'white' }}>
                            {anime.episodes} episodios
                          </Text>
                        )}
                      </Space>
                    </Space>
                  </Col>
                </Row>
              </div>
            </div>
          </div>
        ))}
      </Carousel>
    </Card>
  );
};
