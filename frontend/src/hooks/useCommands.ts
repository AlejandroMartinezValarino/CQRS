import { useState } from 'react';
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

  const registerClick = async (command: ClickCommand) => {
    setLoading(true);
    try {
      await commandService.registerClick(command);
      message.success('Click registrado correctamente');
      scheduleReadModelRefetch(client);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Error al registrar click');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const registerView = async (command: ViewCommand) => {
    setLoading(true);
    try {
      await commandService.registerView(command);
      message.success('Visualización registrada correctamente');
      scheduleReadModelRefetch(client);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Error al registrar visualización');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const registerRating = async (command: RatingCommand) => {
    setLoading(true);
    try {
      await commandService.registerRating(command);
      message.success('Calificación registrada correctamente');
      scheduleReadModelRefetch(client);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Error al registrar calificación');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    registerClick,
    registerView,
    registerRating,
  };
};
