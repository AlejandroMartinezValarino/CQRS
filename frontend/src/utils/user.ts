const STORAGE_KEY = 'cqrs_user_id';

export const getUserId = (): string => {
  if (typeof localStorage === 'undefined') {
    return 'anon';
  }
  let userId = localStorage.getItem(STORAGE_KEY);
  if (!userId) {
    userId = `user-${Date.now().toString(36)}-${Math.random().toString(16).slice(2, 8)}`;
    localStorage.setItem(STORAGE_KEY, userId);
  }
  return userId;
};
