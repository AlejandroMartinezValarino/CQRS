import { useCallback, useEffect, useRef } from 'react';
import { sendClick, sendView } from '@/utils/interactions';

export const useAutoInteractions = (animeId?: number) => {
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    if (!animeId) return;
    startRef.current = Date.now();

    return () => {
      if (!animeId || !startRef.current) return;
      const elapsed = Math.max(1, Math.round((Date.now() - startRef.current) / 1000));
      sendView(animeId, elapsed);
    };
  }, [animeId]);

  const trackClick = useCallback(() => {
    if (!animeId) return;
    sendClick(animeId);
  }, [animeId]);

  return { trackClick };
};
