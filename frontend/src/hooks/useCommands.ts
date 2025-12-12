import { useState } from 'react';
import { message } from 'antd';
import { commandService } from '@/services/api/commands';
import type { ClickCommand, ViewCommand, RatingCommand } from '@/types/commands';

export const useCommands = () => {
  const [loading, setLoading] = useState(false);

  const registerClick = async (command: ClickCommand) => {
    setLoading(true);
    try {
      await commandService.registerClick(command);
      message.success('Click registrado correctamente');
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
