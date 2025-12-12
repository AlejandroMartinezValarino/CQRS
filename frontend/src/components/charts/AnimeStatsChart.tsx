import { Column } from '@ant-design/charts';
import type { AnimeStats } from '@/types/anime';

interface AnimeStatsChartProps {
  data: AnimeStats[];
  title: string;
}

export const AnimeStatsChart = ({ data, title }: AnimeStatsChartProps) => {
  const config = {
    data,
    xField: 'animeId',
    yField: 'totalViews',
    columnWidthRatio: 0.6,
    meta: {
      animeId: { alias: 'Anime ID' },
      totalViews: { alias: 'Visualizaciones' },
    },
    label: {
      position: 'middle' as const,
      style: {
        fill: '#FFFFFF',
        opacity: 0.6,
      },
    },
  };

  return (
    <div>
      <h3>{title}</h3>
      <Column {...config} />
    </div>
  );
};
