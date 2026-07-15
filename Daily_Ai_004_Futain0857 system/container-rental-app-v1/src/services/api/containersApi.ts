import { Container } from '../../types/container';
import { callGasApi } from './gasClient';

const TABLE_NAME = 'containers';

export async function listContainers(): Promise<Container[]> {
  return callGasApi<Container[]>('list', { table: TABLE_NAME });
}

export async function createContainer(
  containerData: Omit<Container, 'container_id' | 'created_at' | 'updated_at'>
): Promise<Container> {
  return callGasApi<Container>('create', { table: TABLE_NAME, data: containerData });
}

export async function updateContainer(
  id: string,
  updates: Partial<Omit<Container, 'container_id' | 'created_at'>>
): Promise<Container> {
  return callGasApi<Container>('update', { table: TABLE_NAME, id, updates });
}

export async function deleteContainer(id: string): Promise<void> {
  await callGasApi('softDelete', { table: TABLE_NAME, id });
}
