const ACTING_USER_STORAGE_KEY = "windconfig_acting_user";
export const DEFAULT_ACTING_USER = "Demo User";

export function getActingUser(): string {
  try {
    const stored = window.localStorage.getItem(ACTING_USER_STORAGE_KEY);
    return stored && stored.trim() ? stored.trim() : DEFAULT_ACTING_USER;
  } catch {
    return DEFAULT_ACTING_USER;
  }
}

export function setActingUser(userName: string): void {
  try {
    window.localStorage.setItem(ACTING_USER_STORAGE_KEY, userName);
  } catch {
    // Ignore storage errors in restricted environments
  }
}
