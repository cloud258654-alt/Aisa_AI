import { CustomerLedger } from '../../types/customerLedger';
import { db } from '../firebase/firebase';
import { collection, getDocs, doc, setDoc, updateDoc } from 'firebase/firestore';
import { generateLocalId } from '../../utils/ids';
import { format } from 'date-fns';

const COLLECTION_NAME = 'customer_ledgers';

export async function listCustomerLedgers(): Promise<CustomerLedger[]> {
  try {
    const colRef = collection(db, COLLECTION_NAME);
    const querySnapshot = await getDocs(colRef);
    const list: CustomerLedger[] = [];
    
    querySnapshot.forEach((docSnap) => {
      const data = docSnap.data() as CustomerLedger;
      list.push(data);
    });

    return list.filter(cl => !cl.deleted_at);
  } catch (error) {
    console.error("Firestore listCustomerLedgers failed:", error);
    throw error;
  }
}

export async function createCustomerLedgerEntry(
  entryData: Omit<CustomerLedger, 'ledger_id' | 'created_at' | 'updated_at'>
): Promise<void> {
  const ledgerId = generateLocalId('CL');
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  const entry: CustomerLedger = {
    ...entryData,
    ledger_id: ledgerId,
    created_at: nowStr,
    updated_at: nowStr,
  };

  try {
    const docRef = doc(db, COLLECTION_NAME, ledgerId);
    await setDoc(docRef, entry);
    return entry;
  } catch (error) {
    console.error("Firestore createCustomerLedgerEntry failed:", error);
    throw error;
  }
}

export async function updateCustomerLedgerEntry(
  id: string,
  updates: Partial<Omit<CustomerLedger, 'ledger_id' | 'created_at'>>
): Promise<CustomerLedger> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    const updatePayload = {
      ...updates,
      updated_at: nowStr
    };
    await updateDoc(docRef, updatePayload);
  } catch (error) {
    console.error("Firestore updateCustomerLedgerEntry failed:", error);
    throw error;
  }
}

export async function deleteCustomerLedgerEntry(id: string): Promise<void> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    await updateDoc(docRef, {
      deleted_at: nowStr,
      updated_at: nowStr
    });
  } catch (error) {
    console.error("Firestore deleteCustomerLedgerEntry failed:", error);
    throw error;
  }
}
