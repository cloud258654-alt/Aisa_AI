import { doc, getDoc } from 'firebase/firestore';
import { db } from '../firebase/firebase';
import { isUserRole, type UserProfile } from '../../types/userProfile';

export class UserProfileError extends Error {}

export async function getUserProfile(uid: string): Promise<UserProfile> {
  const snapshot = await getDoc(doc(db, 'users', uid));
  if (!snapshot.exists()) throw new UserProfileError('找不到使用者權限設定，請聯絡系統管理員。');
  const data = snapshot.data();
  if (!isUserRole(data.role) || (data.status !== 'active' && data.status !== 'disabled')) {
    throw new UserProfileError('使用者權限設定格式無效，請聯絡系統管理員。');
  }
  return { ...data, uid } as UserProfile;
}
