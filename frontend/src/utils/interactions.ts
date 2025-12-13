import { commandService } from '@/services/api/commands';
import { getUserId } from './user';

export const sendClick = async (animeId: number) => {
  try {
    await commandService.registerClick({
      anime_id: animeId,
      user_id: getUserId(),
    });
  } catch (error) {
    console.warn('No se pudo registrar el click', error);
  }
};

export const sendView = async (animeId: number, durationSeconds: number) => {
  try {
    await commandService.registerView({
      anime_id: animeId,
      user_id: getUserId(),
      duration_seconds: durationSeconds,
    });
  } catch (error) {
    console.warn('No se pudo registrar la visualización', error);
  }
};
