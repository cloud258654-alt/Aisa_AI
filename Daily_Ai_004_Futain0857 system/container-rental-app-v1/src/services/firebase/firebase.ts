import { initializeApp } from 'firebase/app';
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

// Helper to get configuration dynamically (supporting localStorage fallback for settings page)
export function getFirebaseConfig() {
  return {
    apiKey: localStorage.getItem('container_rental_firebase_api_key') || import.meta.env.VITE_FIREBASE_API_KEY || "",
    authDomain: localStorage.getItem('container_rental_firebase_auth_domain') || import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
    projectId: localStorage.getItem('container_rental_firebase_project_id') || import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
    storageBucket: localStorage.getItem('container_rental_firebase_storage_bucket') || import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "",
    messagingSenderId: localStorage.getItem('container_rental_firebase_messaging_sender_id') || import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
    appId: localStorage.getItem('container_rental_firebase_app_id') || import.meta.env.VITE_FIREBASE_APP_ID || ""
  };
}

const config = getFirebaseConfig();

// Initialize Firebase App
const app = initializeApp(config);

// Initialize Firestore with local multi-tab cache persistence (Firebase v10+ SDK standard)
const db = initializeFirestore(app, {
  localCache: persistentLocalCache({
    tabManager: persistentMultipleTabManager()
  })
});

// Initialize Auth
const auth = getAuth(app);

export { db, app, auth };
export default db;
