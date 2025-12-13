import { useState, useEffect, useRef } from 'react';
import { Row, Col, Radio, Spin, Empty, Typography } from 'antd';
import { AppstoreOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useSearchAnimes } from '@/hooks/useGraphQL';
import { AnimeCard } from '@/components/anime/AnimeCard';
import { SearchBar } from '@/components/anime/SearchBar';
import { FilterPanel } from '@/components/anime/FilterPanel';
import { TrendingSection } from '@/components/anime/TrendingSection';
import type { AnimeFilters } from '@/types/anime';
import { sendClick } from '@/utils/interactions';

const { Title } = Typography;

type ViewMode = 'grid' | 'list';

export const AnimeList = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<AnimeFilters>({ sortBy: 'popularity' });
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [allItems, setAllItems] = useState<any[]>([]);
  const observerTarget = useRef<HTMLDivElement>(null);

  const { data, loading } = useSearchAnimes(page, 20, filters);

  useEffect(() => {
    setPage(1);
    setAllItems([]);
  }, [filters]);

  useEffect(() => {
    if (data?.searchAnimes?.items) {
      if (page === 1) {
        setAllItems(data.searchAnimes.items);
      } else {
        setAllItems((prev) => [...prev, ...data.searchAnimes.items]);
      }
    }
  }, [data, page]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && data?.searchAnimes?.hasMore && !loading) {
          setPage((p) => p + 1);
        }
      },
      { threshold: 1.0 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [data, loading]);

  const handleSearch = (value: string) => {
    setFilters((prev) => ({ ...prev, search: value || undefined }));
  };

  const handleAnimeSelect = (_value: string, anime: any) => {
    sendClick(anime.myanimelistId);
    navigate(`/animes/${anime.myanimelistId}`);
  };

  return (
    <div style={{ padding: 24 }}>
      <TrendingSection />

      <Row gutter={24}>
        <Col xs={24} lg={6}>
          <FilterPanel filters={filters} onFiltersChange={setFilters} />
        </Col>

        <Col xs={24} lg={18}>
          <div style={{ marginBottom: 24 }}>
            <SearchBar onSearch={handleSearch} onSelect={handleAnimeSelect} />
          </div>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
          }}>
            <Title level={5} style={{ margin: 0 }}>
              {data?.searchAnimes?.total
                ? `${data.searchAnimes.total} animes encontrados`
                : 'Cargando...'}
            </Title>
            <Radio.Group
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              buttonStyle="solid"
            >
              <Radio.Button value="grid">
                <AppstoreOutlined />
              </Radio.Button>
              <Radio.Button value="list">
                <UnorderedListOutlined />
              </Radio.Button>
            </Radio.Group>
          </div>

          {allItems.length === 0 && !loading ? (
            <Empty description="No se encontraron animes" />
          ) : (
            <>
              <Row gutter={[16, 16]}>
                {allItems.map((anime) => (
                  <Col
                    key={anime.myanimelistId}
                    xs={24}
                    sm={viewMode === 'grid' ? 12 : 24}
                    md={viewMode === 'grid' ? 8 : 24}
                    lg={viewMode === 'grid' ? 8 : 24}
                    xl={viewMode === 'grid' ? 6 : 24}
                  >
                    <AnimeCard
                      anime={anime}
                      onClick={() => {
                        sendClick(anime.myanimelistId);
                        navigate(`/animes/${anime.myanimelistId}`);
                      }}
                    />
                  </Col>
                ))}
              </Row>

              <div ref={observerTarget} style={{ height: 20, margin: '20px 0' }} />

              {loading && (
                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                  <Spin size="large" />
                </div>
              )}
            </>
          )}
        </Col>
      </Row>
    </div>
  );
};
