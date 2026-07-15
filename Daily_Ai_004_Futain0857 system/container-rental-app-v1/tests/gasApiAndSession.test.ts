import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { occupancyRate, monthlyRentCollected, unpaidRent, depositBalance, expiringRentalsWithinDays } from '../src/utils/dashboardCalculations';
import { callGasApi } from '../src/services/api/gasClient';
import { CustomerLedger } from '../src/types/customerLedger';
import { RentalRecord } from '../src/types/rentalRecord';
import { Container } from '../src/types/container';

const mockLedger = (overrides: Partial<CustomerLedger>): CustomerLedger => ({
  ledger_id: '1',
  rental_id: 'r1',
  customer_id: 'c1',
  container_id: 'x1',
  event_type: 'rent',
  amount: 100,
  paid_status: 'paid',
  period_start: '',
  period_end: '',
  due_date: '',
  paid_date: '2026-07-10',
  payment_method: '',
  receipt_no: '',
  note: '',
  created_at: '',
  updated_at: '',
  ...overrides
});

describe('Dashboard Math Calculations', () => {
  it('should compute occupancy rate correctly', () => {
    const containers: Partial<Container>[] = [
      { status: 'rented' },
      { status: 'available' },
      { status: 'maintenance' },
      { status: 'retired' } // retired is excluded from denominator
    ];
    expect(occupancyRate(containers as Container[])).toBe(1/3); // rented (1) / active (3)
  });

  it('should calculate monthly rent collected for the current month', () => {
    const entries: CustomerLedger[] = [
      mockLedger({ paid_status: 'paid', paid_date: '2026-07-12', amount: 500 }),
      mockLedger({ paid_status: 'paid', paid_date: '2026-06-12', amount: 300 }), // different month
      mockLedger({ paid_status: 'unpaid', paid_date: '', amount: 500 }), // unpaid
    ];
    expect(monthlyRentCollected(entries, new Date('2026-07-15'))).toBe(500);
  });

  it('should calculate unpaid rent', () => {
    const entries: CustomerLedger[] = [
      mockLedger({ paid_status: 'unpaid', amount: 400 }),
      mockLedger({ paid_status: 'partial', amount: 150 }),
      mockLedger({ paid_status: 'paid', amount: 500 }),
    ];
    expect(unpaidRent(entries)).toBe(550);
  });

  it('should calculate deposit balance based on paid deposit_in and deposit_out', () => {
    const entries: CustomerLedger[] = [
      mockLedger({ event_type: 'deposit_in', paid_status: 'paid', amount: 1000 }),
      mockLedger({ event_type: 'deposit_out', paid_status: 'paid', amount: 300 }),
      mockLedger({ event_type: 'deposit_in', paid_status: 'unpaid', amount: 500 }), // unpaid
    ];
    expect(depositBalance(entries)).toBe(700);
  });

  it('should calculate expiring rentals within 30 days', () => {
    const rentals: Partial<RentalRecord>[] = [
      { status: 'active', end_date: '2026-07-20' },
      { status: 'active', end_date: '2026-08-10' },
      { status: 'ended', end_date: '2026-07-20' }, // already ended
      { status: 'active', end_date: '2026-09-01' } // too far out
    ];
    expect(expiringRentalsWithinDays(rentals as RentalRecord[], 30, new Date('2026-07-14'))).toBe(2);
  });
});

describe('GAS API & Session Handling', () => {
  beforeEach(() => {
    vi.stubGlobal('sessionStorage', {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    });
    vi.stubGlobal('window', {
      dispatchEvent: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  it('should successfully parse GAS API response', async () => {
    const mockResponse = {
      ok: true,
      data: { success: true },
      error: null
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });
    vi.stubGlobal('fetch', fetchMock);

    // Stub VITE_GAS_WEB_APP_URL
    vi.stubEnv('VITE_GAS_WEB_APP_URL', 'https://mock.url/exec');

    const data = await callGasApi<{ success: boolean }>('testAction');
    expect(data).toEqual({ success: true });
    expect(fetchMock).toHaveBeenCalled();
  });

  it('should throw unauthorized error and dispatch session-expired event on UNAUTHORIZED code', async () => {
    const mockResponse = {
      ok: false,
      data: null,
      error: {
        code: 'UNAUTHORIZED',
        message: '登入已逾期'
      }
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse
    });
    vi.stubGlobal('fetch', fetchMock);
    vi.stubEnv('VITE_GAS_WEB_APP_URL', 'https://mock.url/exec');

    const dispatchMock = vi.fn();
    vi.stubGlobal('window', {
      dispatchEvent: dispatchMock,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    });

    await expect(callGasApi<unknown>('testAction')).rejects.toThrow('登入已逾期');
    expect(dispatchMock).toHaveBeenCalledWith(expect.any(Event));
  });

  it('should handle network failures correctly', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
    vi.stubGlobal('fetch', fetchMock);
    vi.stubEnv('VITE_GAS_WEB_APP_URL', 'https://mock.url/exec');

    await expect(callGasApi<unknown>('testAction')).rejects.toThrow('網路連線失敗，無法與伺服器建立連接，請確認網路連線');
  });

  it('should fail if GAS Web App URL is missing', async () => {
    vi.stubEnv('VITE_GAS_WEB_APP_URL', '');
    await expect(callGasApi<unknown>('testAction')).rejects.toThrow('未設定後端 API 網址');
  });
});
