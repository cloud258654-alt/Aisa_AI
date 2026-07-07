import { format } from 'date-fns';

/**
 * Generate a unique ID with format PREFIX-YYYYMMDD-XXXX
 * where XXXX is a random 4-digit number (for high probability uniqueness)
 */
export function generateLocalId(prefix: 'CUST' | 'CONT' | 'RENT' | 'CL' | 'ML'): string {
  const yyyymmdd = format(new Date(), 'yyyyMMdd');
  const rand = Math.floor(1000 + Math.random() * 9000); // 1000 to 9999
  return `${prefix}-${yyyymmdd}-${rand}`;
}
