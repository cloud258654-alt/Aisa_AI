import { readFileSync } from 'node:fs';
import { afterAll, beforeAll, beforeEach, describe, it } from 'vitest';
import { assertFails, assertSucceeds, initializeTestEnvironment, type RulesTestEnvironment } from '@firebase/rules-unit-testing';
import { doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';
let env: RulesTestEnvironment;
const profile = (role: string, status = 'active') => ({ uid: role, email: `${role}@test.local`, display_name: role, role, status, created_at: '', updated_at: '' });
beforeAll(async () => { env = await initializeTestEnvironment({ projectId: 'demo-container-rental', firestore: { rules: readFileSync('firestore.rules', 'utf8'), host: '127.0.0.1', port: 8080 } }); });
beforeEach(async () => { await env.clearFirestore(); });
afterAll(async () => { await env.cleanup(); });
async function seed(uid: string, role: string, status = 'active') { await env.withSecurityRulesDisabled(async (context) => setDoc(doc(context.firestore(), 'users', uid), { ...profile(role, status), uid })); }
describe('Firestore rules', () => {
  it('denies unauthenticated and profile-less access', async () => { await assertFails(getDoc(doc(env.unauthenticatedContext().firestore(), 'customers', 'c'))); await assertFails(getDoc(doc(env.authenticatedContext('none').firestore(), 'customers', 'c'))); });
  it('denies disabled users', async () => { await seed('disabled', 'staff', 'disabled'); await assertFails(getDoc(doc(env.authenticatedContext('disabled').firestore(), 'customers', 'c'))); });
  it('allows admin full data and user administration', async () => { await seed('admin', 'admin'); const db = env.authenticatedContext('admin').firestore(); await assertSucceeds(setDoc(doc(db, 'customers', 'c'), { name: 'x' })); await assertSucceeds(setDoc(doc(db, 'users', 'staff'), { ...profile('staff'), uid: 'staff' })); });
  it('prevents manager from changing roles', async () => { await seed('manager', 'manager'); await seed('staff', 'staff'); await assertFails(updateDoc(doc(env.authenticatedContext('manager').firestore(), 'users', 'staff'), { role: 'admin' })); });
  it('lets finance update ledgers but not containers', async () => { await seed('finance', 'finance'); const db = env.authenticatedContext('finance').firestore(); await assertSucceeds(setDoc(doc(db, 'customer_ledgers', 'l'), { amount: 1 })); await assertFails(setDoc(doc(db, 'containers', 'c'), { status: 'available' })); });
  it('lets staff edit customers and non-financial container fields, but not rentals, ledgers or costs', async () => {
    await seed('staff2', 'staff');
    await env.withSecurityRulesDisabled(async (context) => setDoc(doc(context.firestore(), 'containers', 'c'), { container_no: 'A1', total_setup_cost: 100, status: 'available' }));
    const db = env.authenticatedContext('staff2').firestore();
    await assertSucceeds(setDoc(doc(db, 'customers', 'c'), { name: 'x' }));
    await assertSucceeds(updateDoc(doc(db, 'containers', 'c'), { status: 'maintenance' }));
    await assertFails(updateDoc(doc(db, 'containers', 'c'), { total_setup_cost: 1 }));
    await assertFails(setDoc(doc(db, 'rental_records', 'r'), { status: 'active' }));
    await assertFails(setDoc(doc(db, 'customer_ledgers', 'l'), { amount: 1 }));
  });
  it('prevents normal users escalating their own role', async () => { await seed('self', 'staff'); await assertFails(updateDoc(doc(env.authenticatedContext('self').firestore(), 'users', 'self'), { role: 'admin' })); });
});
