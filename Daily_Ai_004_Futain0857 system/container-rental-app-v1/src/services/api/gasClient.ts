export interface GasError {
  code: string;
  message: string;
}

export interface GasResponse<T> {
  ok: boolean;
  data: T | null;
  error: GasError | null;
}

export type GasPayload = Record<string, unknown>;

/**
 * Extract message safely from unknown error object
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  return '未知錯誤';
}

/**
 * Execute request to Google Apps Script Web App
 */
export async function callGasApi<T>(action: string, payload: GasPayload = {}): Promise<T> {
  const gasWebAppUrl = import.meta.env.VITE_GAS_WEB_APP_URL || '';
  if (!gasWebAppUrl) {
    throw new Error('系統設定錯誤：未設定後端 API 網址 (VITE_GAS_WEB_APP_URL)。');
  }

  // Get session token from sessionStorage
  const sessionToken = sessionStorage.getItem('sessionToken');

  const requestBody = {
    action,
    sessionToken: sessionToken || '',
    payload
  };

  try {
    const response = await fetch(gasWebAppUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain;charset=utf-8',
      },
      body: JSON.stringify(requestBody),
      redirect: 'follow', // Automatically follow GAS 302 redirects
    });

    if (!response.ok) {
      throw new Error(`連線失敗 (HTTP ${response.status})，請檢查網路狀態。`);
    }

    const resJson = (await response.json()) as GasResponse<T>;

    if (!resJson.ok) {
      // Check for unauthorized access
      if (resJson.error?.code === 'UNAUTHORIZED') {
        sessionStorage.removeItem('sessionToken');
        sessionStorage.removeItem('sessionExpiresAt');
        // Redirect to login or dispatch session expiry event
        window.dispatchEvent(new Event('session-expired'));
        throw new Error(resJson.error.message || '登入已逾期，請重新登入。');
      }
      throw new Error(resJson.error?.message || '未知後端錯誤');
    }

    if (resJson.data === null) {
      throw new Error('未收到有效的資料回傳');
    }

    return resJson.data;
  } catch (error: unknown) {
    console.error(`GAS API [${action}] failed:`, error);
    const message = getErrorMessage(error);
    // Standardize error message for frontend
    if (message.includes('Failed to fetch')) {
      throw new Error('網路連線失敗，無法與伺服器建立連接，請確認網路連線。');
    }
    throw error;
  }
}
