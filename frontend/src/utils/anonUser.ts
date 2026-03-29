const STORAGE_KEY = 'cqrs_anon_user_id';

/** ID estable por navegador para comandos sin login. */
export function getAnonUserId(): string {
  try {
    let id = localStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  } catch {
    return 'anonymous';
  }
}
