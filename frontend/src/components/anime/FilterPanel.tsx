import { Card, Space, Select, Slider, Radio, Divider, Typography } from 'antd';
import { useGenres } from '@/hooks/useGraphQL';
import type { AnimeFilters } from '@/types/anime';

const { Title } = Typography;

interface FilterPanelProps {
  filters: AnimeFilters;
  onFiltersChange: (filters: AnimeFilters) => void;
}

const ANIME_TYPES = ['TV', 'Movie', 'OVA', 'Special', 'ONA', 'Music'];
const SORT_OPTIONS = [
  { label: 'Popularidad', value: 'popularity' },
  { label: 'Puntuación', value: 'score' },
  { label: 'Título', value: 'title' },
  { label: 'Visualizaciones', value: 'views' },
];

export const FilterPanel = ({ filters, onFiltersChange }: FilterPanelProps) => {
  const { data: genresData, loading: genresLoading } = useGenres();

  const handleTypeChange = (value: string | null) => {
    onFiltersChange({ ...filters, type: value || undefined });
  };

  const handleGenresChange = (value: string[]) => {
    onFiltersChange({ ...filters, genres: value.length > 0 ? value : undefined });
  };

  const handleScoreChange = (value: number) => {
    onFiltersChange({ ...filters, minScore: value > 0 ? value : undefined });
  };

  const handleSortChange = (value: any) => {
    onFiltersChange({ ...filters, sortBy: value });
  };

  return (
    <Card
      title={<Title level={5} style={{ margin: 0 }}>Filtros</Title>}
      size="small"
      style={{ position: 'sticky', top: 24 }}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div>
          <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
            Tipo
          </Typography.Text>
          <Select
            placeholder="Todos"
            value={filters.type || null}
            onChange={handleTypeChange}
            style={{ width: '100%' }}
            allowClear
            options={ANIME_TYPES.map(type => ({ label: type, value: type }))}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        <div>
          <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
            Géneros
          </Typography.Text>
          <Select
            mode="multiple"
            placeholder="Seleccionar géneros"
            value={filters.genres || []}
            onChange={handleGenresChange}
            style={{ width: '100%' }}
            loading={genresLoading}
            maxTagCount="responsive"
            options={genresData?.genres?.map(genre => ({ label: genre, value: genre }))}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        <div>
          <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
            Puntuación mínima: {filters.minScore || 0}
          </Typography.Text>
          <Slider
            min={0}
            max={10}
            step={0.5}
            value={filters.minScore || 0}
            onChange={handleScoreChange}
            marks={{
              0: '0',
              5: '5',
              10: '10',
            }}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        <div>
          <Typography.Text strong style={{ display: 'block', marginBottom: 12 }}>
            Ordenar por
          </Typography.Text>
          <Radio.Group
            value={filters.sortBy || 'popularity'}
            onChange={(e) => handleSortChange(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              {SORT_OPTIONS.map(option => (
                <Radio key={option.value} value={option.value}>
                  {option.label}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </div>
      </Space>
    </Card>
  );
};
