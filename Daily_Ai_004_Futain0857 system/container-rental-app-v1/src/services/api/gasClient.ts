export interface GasResponse<T = any> {
  ok: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
  } | null;
}

const GAS_WEB_APP_URL = import.meta.env.VITE_GAS_WEB_APP_URL || '';

/**
 * Execute request to Google Apps Script Web App
 */
export async function callGasApi<T = any>(action: string, payload: any = {}): Promise<T> {
  if (!GAS_WEB_APP_URL) {
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
    const response = await fetch(GAS_WEB_APP_URL, {
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

    const resJson: GasResponse<T> = await response.json();

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

    return resJson.data as T;
  } catch (error: any) {
    console.error(`GAS API [${action}] failed:`, error);
    // Standardize error message for frontend
    if (error.message && error.message.includes('Failed to fetch')) {
      throw new Error('網路連線失敗，無法與伺服器建立連接，請確認網路連線。');
    }
    throw error;
  }
}
