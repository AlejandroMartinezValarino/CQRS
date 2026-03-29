import { useState, useCallback } from 'react';
import { useApolloClient } from '@apollo/client';
import { message } from 'antd';
import { commandService } from '@/services/api/commands';
import {
  TOP_ANIMES_BY_VIEWS,
  TOP_ANIMES_BY_RATING,
  ANIME_STATS,
  ANIME,
} from '@/services/graphql/queries';
import type { ClickCommand, ViewCommand, RatingCommand } from '@/types/commands';

export type CommandOptions = { silent?: boolean };

/** El read model se actualiza vía Kafka → consumer (asíncrono). Refetch al instante y otro tras ~1.5s. */
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

export const useCommands = () => {
  const [loading, setLoading] = useState(false);
  const client = useApolloClient();

  const registerClick = useCallback(
    async (command: ClickCommand, opts?: CommandOptions) => {
      const silent = opts?.silent === true;
      if (!silent) setLoading(true);
      try {
        await commandService.registerClick(command);
        if (!silent) message.success('Click registrado correctamente');
        scheduleReadModelRefetch(client);
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        if (!silent) {
          message.error(err.response?.data?.detail || 'Error al registrar click');
        }
        throw error;
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [client]
  );

  const registerView = useCallback(
    async (command: ViewCommand, opts?: CommandOptions) => {
      const silent = opts?.silent === true;
      if (!silent) setLoading(true);
      try {
        await commandService.registerView(command);
        if (!silent) message.success('Visualización registrada correctamente');
        scheduleReadModelRefetch(client);
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        if (!silent) {
          message.error(err.response?.data?.detail || 'Error al registrar visualización');
        }
        throw error;
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [client]
  );

  const registerRating = useCallback(
    async (command: RatingCommand, opts?: CommandOptions) => {
      const silent = opts?.silent === true;
      if (!silent) setLoading(true);
      try {
        await commandService.registerRating(command);
        if (!silent) message.success('Calificación registrada correctamente');
        scheduleReadModelRefetch(client);
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        if (!silent) {
          message.error(err.response?.data?.detail || 'Error al registrar calificación');
        }
        throw error;
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [client]
  );

  return {
    loading,
    registerClick,
    registerView,
    registerRating,
  };
};
