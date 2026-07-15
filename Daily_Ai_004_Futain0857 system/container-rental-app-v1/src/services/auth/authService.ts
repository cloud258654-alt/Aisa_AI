import { callGasApi } from '../api/gasClient';

export interface LoginResult {
  sessionToken: string;
  expiresAt: string;
}

export async function loginAdmin(username: string, password: string): Promise<LoginResult> {
  return callGasApi<LoginResult>('login', { username, password });
}

export async function logoutAdmin(token: string): Promise<void> {
  try {
    await callGasApi('logout', { sessionToken: token });
  } catch (error) {
    console.warn("Logout request failed on server, cleaning local session anyway.", error);
  }
}
