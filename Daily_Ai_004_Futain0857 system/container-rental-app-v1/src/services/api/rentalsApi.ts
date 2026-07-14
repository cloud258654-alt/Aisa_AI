import { RentalRecord } from '../../types/rentalRecord';
import { CustomerLedger } from '../../types/customerLedger';
import { db } from '../firebase/firebase';
import { collection, getDocs, doc, writeBatch, updateDoc, runTransaction } from 'firebase/firestore';
import { generateLocalId } from '../../utils/ids';
import { format, addMonths, subDays, parseISO } from 'date-fns';

const COLLECTION_NAME = 'rental_records';

export async function listRentals(): Promise<RentalRecord[]> {
  try {
    const colRef = collection(db, COLLECTION_NAME);
    const querySnapshot = await getDocs(colRef);
    const list: RentalRecord[] = [];
    
    querySnapshot.forEach((docSnap) => {
      const data = docSnap.data() as RentalRecord;
      list.push(data);
    });

    return list.filter(r => !r.deleted_at);
  } catch (error) {
    console.error("Firestore listRentals failed:", error);
    throw error;
  }
}

export async function createRental(
  rentalData: Omit<RentalRecord, 'rental_id' | 'created_at' | 'updated_at'>,
  createFirstMonthBill: boolean
): Promise<void> {
  const rentalId = generateLocalId('RENT');
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  const rental: RentalRecord = {
    ...rentalData,
    rental_id: rentalId,
    created_at: nowStr,
    updated_at: nowStr,
  };

  try {
    // 1. 防呆：先讀取所有租賃紀錄，確保該貨櫃目前沒有任何 active 租約
    const currentRentals = await listRentals();
    const activeForContainer = currentRentals.some(r => r.container_id === rental.container_id && r.status === 'active');
    if (activeForContainer) {
      throw new Error(`該貨櫃 (${rental.container_id}) 目前已有生效中的合約，無法重複承租！`);
    }

    // 2. 啟動交易 (Transaction)
    await runTransaction(db, async (transaction) => {
      // 讀取貨櫃資訊，檢查 status 是否為 available
      const containerRef = doc(db, 'containers', rental.container_id);
      const containerSnap = await transaction.get(containerRef);
      if (!containerSnap.exists()) {
        throw new Error("指定貨櫃不存在！");
      }
      
      const containerStatus = containerSnap.data().status;
      if (containerStatus !== 'available') {
        const containerNo = containerSnap.data().container_no || '未知';
        throw new Error(`貨櫃 ${containerNo} 狀態為「${containerStatus === 'rented' ? '出租中' : containerStatus === 'maintenance' ? '維修中' : '已停用'}」，不可出租！`);
      }

      // 執行寫入
      // A. 新增租賃合約
      const rentalRef = doc(db, COLLECTION_NAME, rentalId);
      transaction.set(rentalRef, rental);

      // B. 更新貨櫃狀態為 rented
      transaction.update(containerRef, {
        status: 'rented',
        updated_at: nowStr
      });

      // C. 新增首期租金與押金帳務
      if (createFirstMonthBill) {
        const startDate = parseISO(rental.start_date);
        const firstMonthEndDate = subDays(addMonths(startDate, 1), 1);
        const firstMonthEndDateStr = format(firstMonthEndDate, 'yyyy-MM-dd');

        // Pay due date
        let dueDateStr = rental.start_date;
        try {
          const dueDay = rental.payment_due_day;
          const targetDueDate = new Date(startDate.getFullYear(), startDate.getMonth(), dueDay);
          dueDateStr = format(targetDueDate, 'yyyy-MM-dd');
        } catch {
          dueDateStr = rental.start_date;
        }

        // Deposit (deposit_in)
        if (rental.deposit_amount > 0) {
          const depositId = generateLocalId('CL');
          const depositEntry: CustomerLedger = {
            ledger_id: depositId,
            rental_id: rentalId,
            customer_id: rental.customer_id,
            container_id: rental.container_id,
            event_type: 'deposit_in',
            amount: rental.deposit_amount,
            paid_status: 'unpaid',
            period_start: rental.start_date,
            period_end: rental.start_date,
            due_date: rental.start_date,
            paid_date: '',
            payment_method: '',
            receipt_no: '',
            note: '租賃押金應收',
            created_at: nowStr,
            updated_at: nowStr
          };
          const depositRef = doc(db, 'customer_ledgers', depositId);
          transaction.set(depositRef, depositEntry);
        }

        // First Month Rent (rent)
        if (rental.monthly_rent > 0) {
          const rentId = generateLocalId('CL');
          const rentEntry: CustomerLedger = {
            ledger_id: rentId,
            rental_id: rentalId,
            customer_id: rental.customer_id,
            container_id: rental.container_id,
            event_type: 'rent',
            amount: rental.monthly_rent,
            paid_status: 'unpaid',
            period_start: rental.start_date,
            period_end: firstMonthEndDateStr,
            due_date: dueDateStr,
            paid_date: '',
            payment_method: '',
            receipt_no: '',
            note: `首期租金 (${rental.start_date} ~ ${firstMonthEndDateStr})`,
            created_at: nowStr,
            updated_at: nowStr
          };
          const rentRef = doc(db, 'customer_ledgers', rentId);
          transaction.set(rentRef, rentEntry);
        }
      }
    });

    return rental;
  } catch (error) {
    console.error("Firestore createRental runTransaction failed:", error);
    throw error;
  }
}

export async function updateRental(
  id: string,
  updates: Partial<Omit<RentalRecord, 'rental_id' | 'created_at'>>
): Promise<RentalRecord> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    const updatePayload = {
      ...updates,
      updated_at: nowStr
    };
    await updateDoc(docRef, updatePayload);
  } catch (error) {
    console.error("Firestore updateRental failed:", error);
    throw error;
  }
}

export async function terminateRental(
  id: string,
  endedDate: string,
  note?: string
): Promise<RentalRecord> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    // We need the container ID to liberate it
    const list = await listRentals();
    const existing = list.find(r => r.rental_id === id);
    if (!existing) {
      throw new Error(`Rental record with ID ${id} not found.`);
    }

    const batch = writeBatch(db);

    // 1. Update rental status to ended
    const rentalRef = doc(db, COLLECTION_NAME, id);
    const terminatedNote = note ? `${existing.note}\n退租備註: ${note}` : existing.note;
    batch.update(rentalRef, {
      status: 'ended',
      ended_date: endedDate,
      note: terminatedNote,
      updated_at: nowStr
    });

    // 2. Set container status back to available
    const containerRef = doc(db, 'containers', existing.container_id);
    batch.update(containerRef, {
      status: 'available',
      updated_at: nowStr
    });

    await batch.commit();

    return {
      ...existing,
      status: 'ended',
      ended_date: endedDate,
      note: terminatedNote,
      updated_at: nowStr
    };
  } catch (error) {
    console.error("Firestore terminateRental failed:", error);
    throw error;
  }
}

export async function deleteRental(id: string): Promise<void> {
  const nowStr = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  
  try {
    const docRef = doc(db, COLLECTION_NAME, id);
    await updateDoc(docRef, {
      deleted_at: nowStr,
      updated_at: nowStr
    });
  } catch (error) {
    console.error("Firestore deleteRental failed:", error);
    throw error;
  }
}
