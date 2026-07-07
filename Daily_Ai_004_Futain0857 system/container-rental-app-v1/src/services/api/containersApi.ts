import { Container } from '../../types/container';
import { db } from '../firebase/firebase';
import { collection, getDocs, doc, setDoc, updateDoc } from 'firebase/firestore';
import { generateLocalId } from '../../utils/ids';
import { format } from 'date-fns';

const COLLECTION_NAME = 'containers';

export async function listContainers(): Promise<Container[]> {
  try {
    const colRef = collection(db, COLLECTION_NAME);
    const querySnapshot = await getDocs(colRef);
    const list: Container[] = [];
    
    querySnapshot.forEach((docSnap) => {
      const data = docSnap.data() as Container;
      list.push(data);
    });

    return list.filter(c => !c.deleted_at);
  } catch (error) {
    console.error("Firestore listContainers failed:", error);
    throw error;
  }
}

export async function createContainer(
  containerData: Omit<Container, 'container_id' | 'created_at' | 'updated_at'>
): Promise<Container> {
  const containerId = generateLocalId('CONT');
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  const container: Container = {
    ...containerData,
    container_id: containerId,
    created_at: nowStr,
    updated_at: nowStr,
  };

  try {
    const docRef = doc(db, COLLECTION_NAME, containerId);
    await setDoc(docRef, container);
    return container;
  } catch (error) {
    console.error("Firestore createContainer failed:", error);
    throw error;
  }
}

export async function updateContainer(
  id: string,
  updates: Partial<Omit<Container, 'container_id' | 'created_at'>>
): Promise<Container> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    const updatePayload = {
      ...updates,
      updated_at: nowStr
    };
    await updateDoc(docRef, updatePayload);
    return {
      container_id: id,
      ...updatePayload
    } as any;
  } catch (error) {
    console.error("Firestore updateContainer failed:", error);
    throw error;
  }
}

export async function deleteContainer(id: string): Promise<void> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    await updateDoc(docRef, {
      deleted_at: nowStr,
      updated_at: nowStr
    });
  } catch (error) {
    console.error("Firestore deleteContainer failed:", error);
    throw error;
  }
}
