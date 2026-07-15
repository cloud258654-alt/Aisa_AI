import { RentalRecord } from '../../types/rentalRecord';
import { callGasApi } from './gasClient';

const TABLE_NAME = 'rental_records';

export async function listRentals(): Promise<RentalRecord[]> {
  return callGasApi<RentalRecord[]>('list', { table: TABLE_NAME });
}

export async function createRental(
  rentalData: Omit<RentalRecord, 'rental_id' | 'created_at' | 'updated_at'>,
  createFirstMonthBill: boolean
): Promise<RentalRecord> {
  return callGasApi<RentalRecord>('create', { 
    table: TABLE_NAME, 
    data: rentalData,
    createFirstMonthBill
  });
}

export async function updateRental(
  id: string,
  updates: Partial<Omit<RentalRecord, 'rental_id' | 'created_at'>>
): Promise<RentalRecord> {
  return callGasApi<RentalRecord>('update', { table: TABLE_NAME, id, updates });
}

export async function terminateRental(
  id: string,
  endedDate: string,
  note?: string
): Promise<RentalRecord> {
  return callGasApi<RentalRecord>('terminateRental', { id, endedDate, note });
}

export async function deleteRental(id: string): Promise<void> {
  await callGasApi('softDelete', { table: TABLE_NAME, id });
}
