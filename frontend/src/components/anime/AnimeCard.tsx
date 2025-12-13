import { Card, Tag, Space, Typography } from 'antd';
import { EyeOutlined, LikeOutlined, StarOutlined } from '@ant-design/icons';
import type { AnimeWithStats } from '@/types/anime';
import { formatNumber } from '@/utils';

const { Paragraph, Text } = Typography;

interface AnimeCardProps {
  anime: AnimeWithStats;
  onClick: () => void;
}

export const AnimeCard = ({ anime, onClick }: AnimeCardProps) => {
  const imageUrl = anime.image || '/placeholder-anime.jpg';

  return (
    <Card
      hoverable
      onClick={onClick}
      cover={
        <div style={{
          height: 300,
          overflow: 'hidden',
          position: 'relative',
          backgroundImage: `url(${imageUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}>
          <div style={{
            position: 'absolute',
            top: 8,
            right: 8,
            display: 'flex',
            gap: 4,
            flexDirection: 'column',
            alignItems: 'flex-end',
          }}>
            {anime.type && (
              <Tag color="blue">{anime.type}</Tag>
            )}
            {anime.score && (
              <Tag color="gold" icon={<StarOutlined />}>
                {anime.score.toFixed(1)}
              </Tag>
            )}
          </div>
          <div style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'linear-gradient(transparent, rgba(0,0,0,0.9))',
            padding: '40px 16px 16px',
          }}>
            <Text strong style={{ color: 'white', fontSize: 16 }}>
              {anime.title}
            </Text>
          </div>
        </div>
      }
      bodyStyle={{ padding: 12 }}
    >
      {anime.description && (
        <Paragraph
          ellipsis={{ rows: 2 }}
          style={{ minHeight: 44, marginBottom: 12, fontSize: 12 }}
        >
          {anime.description}
        </Paragraph>
      )}
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        {anime.episodes && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {anime.episodes} episodios
          </Text>
        )}
        <Space size="small" style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space size={4}>
            <EyeOutlined />
            <Text style={{ fontSize: 12 }}>{formatNumber(anime.totalViews)}</Text>
          </Space>
          <Space size={4}>
            <LikeOutlined />
            <Text style={{ fontSize: 12 }}>{formatNumber(anime.totalClicks)}</Text>
          </Space>
          {anime.totalRatings > 0 && (
            <Space size={4}>
              <StarOutlined />
              <Text style={{ fontSize: 12 }}>
                {anime.averageRating?.toFixed(1) || 'N/A'} ({anime.totalRatings})
              </Text>
            </Space>
          )}
        </Space>
      </Space>
    </Card>
  );
};
