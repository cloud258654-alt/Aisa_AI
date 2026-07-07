import { ManagementLedger } from '../../types/managementLedger';
import { db } from '../firebase/firebase';
import { collection, getDocs, doc, setDoc, updateDoc } from 'firebase/firestore';
import { generateLocalId } from '../../utils/ids';
import { format } from 'date-fns';

const COLLECTION_NAME = 'management_ledgers';

export async function listManagementLedgers(): Promise<ManagementLedger[]> {
  try {
    const colRef = collection(db, COLLECTION_NAME);
    const querySnapshot = await getDocs(colRef);
    const list: ManagementLedger[] = [];
    
    querySnapshot.forEach((docSnap) => {
      const data = docSnap.data() as ManagementLedger;
      list.push(data);
    });

    return list.filter(ml => !ml.deleted_at);
  } catch (error) {
    console.error("Firestore listManagementLedgers failed:", error);
    throw error;
  }
}

export async function createManagementLedgerEntry(
  entryData: Omit<ManagementLedger, 'ledger_id' | 'created_at' | 'updated_at'>
): Promise<ManagementLedger> {
  const ledgerId = generateLocalId('ML');
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  const entry: ManagementLedger = {
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
    console.error("Firestore createManagementLedgerEntry failed:", error);
    throw error;
  }
}

export async function updateManagementLedgerEntry(
  id: string,
  updates: Partial<Omit<ManagementLedger, 'ledger_id' | 'created_at'>>
): Promise<ManagementLedger> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    const updatePayload = {
      ...updates,
      updated_at: nowStr
    };
    await updateDoc(docRef, updatePayload);
    return {
      ledger_id: id,
      ...updatePayload
    } as any;
  } catch (error) {
    console.error("Firestore updateManagementLedgerEntry failed:", error);
    throw error;
  }
}

export async function deleteManagementLedgerEntry(id: string): Promise<void> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    await updateDoc(docRef, {
      deleted_at: nowStr,
      updated_at: nowStr
    });
  } catch (error) {
    console.error("Firestore deleteManagementLedgerEntry failed:", error);
    throw error;
  }
}
