import { Customer } from '../../types/customer';
import { callGasApi } from './gasClient';

const TABLE_NAME = 'customers';

export async function listCustomers(): Promise<Customer[]> {
  return callGasApi<Customer[]>('list', { table: TABLE_NAME });
}

export async function createCustomer(
  customerData: Omit<Customer, 'customer_id' | 'created_at' | 'updated_at'>
): Promise<Customer> {
  return callGasApi<Customer>('create', { table: TABLE_NAME, data: customerData });
}

export async function updateCustomer(
  id: string,
  updates: Partial<Omit<Customer, 'customer_id' | 'created_at'>>
): Promise<Customer> {
  return callGasApi<Customer>('update', { table: TABLE_NAME, id, updates });
}

export async function deleteCustomer(id: string): Promise<void> {
  await callGasApi('softDelete', { table: TABLE_NAME, id });
}
