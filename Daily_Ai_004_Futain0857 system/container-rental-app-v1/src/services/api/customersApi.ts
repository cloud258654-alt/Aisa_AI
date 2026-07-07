import { Customer } from '../../types/customer';
import { db } from '../firebase/firebase';
import { collection, getDocs, doc, setDoc, updateDoc } from 'firebase/firestore';
import { generateLocalId } from '../../utils/ids';
import { format } from 'date-fns';

const COLLECTION_NAME = 'customers';

export async function listCustomers(): Promise<Customer[]> {
  try {
    const colRef = collection(db, COLLECTION_NAME);
    const querySnapshot = await getDocs(colRef);
    const list: Customer[] = [];
    
    querySnapshot.forEach((docSnap) => {
      const data = docSnap.data() as Customer;
      list.push(data);
    });

    // Filter out soft-deleted items (having deleted_at)
    return list.filter(c => !c.deleted_at);
  } catch (error) {
    console.error("Firestore listCustomers failed:", error);
    throw error;
  }
}

export async function createCustomer(
  customerData: Omit<Customer, 'customer_id' | 'created_at' | 'updated_at'>
): Promise<Customer> {
  const customerId = generateLocalId('CUST');
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  const customer: Customer = {
    ...customerData,
    customer_id: customerId,
    created_at: nowStr,
    updated_at: nowStr,
  };

  try {
    const docRef = doc(db, COLLECTION_NAME, customerId);
    await setDoc(docRef, customer);
    return customer;
  } catch (error) {
    console.error("Firestore createCustomer failed:", error);
    throw error;
  }
}

export async function updateCustomer(
  id: string,
  updates: Partial<Omit<Customer, 'customer_id' | 'created_at'>>
): Promise<Customer> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    const updatePayload = {
      ...updates,
      updated_at: nowStr
    };
    await updateDoc(docRef, updatePayload);

    // Fetch the updated document to return it
    return {
      customer_id: id,
      ...updatePayload
    } as any;
  } catch (error) {
    console.error("Firestore updateCustomer failed:", error);
    throw error;
  }
}

export async function deleteCustomer(id: string): Promise<void> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    await updateDoc(docRef, {
      deleted_at: nowStr,
      updated_at: nowStr
    });
  } catch (error) {
    console.error("Firestore deleteCustomer failed:", error);
    throw error;
  }
}
