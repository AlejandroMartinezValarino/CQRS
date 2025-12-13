import { useState, useCallback } from 'react';
import { AutoComplete, Input } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useLazyQuery } from '@apollo/client';
import { SEARCH_ANIMES } from '@/services/graphql/queries';
import type { PaginatedAnimes } from '@/types/anime';
import { debounce } from 'lodash-es';

interface SearchBarProps {
  onSearch: (value: string) => void;
  onSelect?: (value: string, anime: any) => void;
}

export const SearchBar = ({ onSearch, onSelect }: SearchBarProps) => {
  const [options, setOptions] = useState<any[]>([]);
  const [searchQuery, { loading }] = useLazyQuery<{ searchAnimes: PaginatedAnimes }>(SEARCH_ANIMES);

  const handleSearch = useCallback(
    debounce(async (value: string) => {
      if (!value || value.length < 2) {
        setOptions([]);
        return;
      }

      try {
        const { data } = await searchQuery({
          variables: {
            page: 1,
            pageSize: 5,
            filters: { search: value },
          },
        });

        if (data?.searchAnimes?.items) {
          const suggestions = data.searchAnimes.items.map((anime) => ({
            value: anime.title,
            label: (
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                {anime.image && (
                  <img
                    src={anime.image}
                    alt={anime.title}
                    style={{ width: 40, height: 60, objectFit: 'cover', borderRadius: 4 }}
                  />
                )}
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500 }}>{anime.title}</div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    {anime.type} • Score: {anime.score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              </div>
            ),
            anime,
          }));
          setOptions(suggestions);
        }
      } catch (error) {
        console.error('Error searching animes:', error);
        setOptions([]);
      }
    }, 300),
    [searchQuery]
  );

  const handleSelect = (value: string, option: any) => {
    if (onSelect && option.anime) {
      onSelect(value, option.anime);
    }
    onSearch(value);
  };

  return (
    <AutoComplete
      options={options}
      onSearch={handleSearch}
      onSelect={handleSelect}
      style={{ width: '100%' }}
    >
      <Input.Search
        size="large"
        placeholder="Buscar anime por título..."
        enterButton={<SearchOutlined />}
        loading={loading}
        onSearch={onSearch}
        allowClear
      />
    </AutoComplete>
  );
};
