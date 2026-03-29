import { useEffect, useRef, useCallback } from 'react';
import { useApolloClient } from '@apollo/client';
import { message } from 'antd';
import { useCommands } from '@/hooks/useCommands';
import { getAnonUserId } from '@/utils/anonUser';
import { formatDuration } from '@/utils';
import {
  TOP_ANIMES_BY_VIEWS,
  TOP_ANIMES_BY_RATING,
  ANIME_STATS,
  ANIME,
} from '@/services/graphql/queries';

function scheduleReadModelRefetch(client: ReturnType<typeof useApolloClient>) {
  const run = () =>
    client
      .refetchQueries({
        include: [TOP_ANIMES_BY_VIEWS, TOP_ANIMES_BY_RATING, ANIME_STATS, ANIME],
      })
      .catch(() => undefined);
  void run();
  setTimeout(run, 1500);
}

/**
 * Click automático al cargar la ficha; al salir envía la visualización con la duración.
 * Cierra de pestaña: fetch keepalive (sin toast). Navegación SPA: axios + toast.
 */
export function useAnimeVisitTracking(
  animeId: number,
  hasLoadedContent: boolean
): void {
  const client = useApolloClient();
  const { registerClick, registerView } = useCommands();
  const startRef = useRef<number>(0);
  const flushedRef = useRef(false);

  const flushDuration = useCallback(
    async (opts: { showToast: boolean; useKeepaliveFetch?: boolean }) => {
      if (flushedRef.current || !Number.isFinite(animeId) || animeId < 1) return;
      flushedRef.current = true;
      const elapsedMs = Date.now() - startRef.current;
      // Cualquier estancia >0 ms cuenta al menos 1 s en el agregado (floor dejaba casi todo en 0).
      const duration =
        elapsedMs <= 0 ? 0 : Math.max(1, Math.ceil(elapsedMs / 1000));
      const userId = getAnonUserId();
      const body = {
        anime_id: animeId,
        user_id: userId,
        duration_seconds: duration,
      };

      if (opts.useKeepaliveFetch) {
        const url = `${window.location.origin}/api/view`;
        try {
          fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            keepalive: true,
          }).catch(() => undefined);
        } catch {
          /* noop */
        }
        return;
      }

      try {
        await registerView(body, { silent: true });
        scheduleReadModelRefetch(client);
        if (opts.showToast) {
          message.info(`Tiempo en esta ficha: ${formatDuration(duration)}`);
        }
      } catch {
        try {
          await fetch(`${window.location.origin}/api/view`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            keepalive: true,
          });
        } catch {
          /* noop */
        }
      }
    },
    [animeId, client, registerView]
  );

  useEffect(() => {
    if (!hasLoadedContent || !Number.isFinite(animeId) || animeId < 1) return;

    startRef.current = Date.now();
    flushedRef.current = false;

    const uid = getAnonUserId();
    void registerClick({ anime_id: animeId, user_id: uid }, { silent: true });

    const onPageHide = () => {
      void flushDuration({ showToast: false, useKeepaliveFetch: true });
    };
    window.addEventListener('pagehide', onPageHide);

    return () => {
      window.removeEventListener('pagehide', onPageHide);
      void flushDuration({ showToast: true, useKeepaliveFetch: false });
    };
  }, [animeId, hasLoadedContent, registerClick, flushDuration]);
}
