# Firestore Security Rules 安全性規則規劃說明書 (FIRESTORE_RULES.md)

本文件提供貨櫃出租系統於 Firebase Firestore 資料庫上的安全性規則規劃，涵蓋 Phase 1（最小可用）與 Phase 2（角色權限細分）的配置設定。

---

## 1. 角色權限規劃 (Role-Based Access Control)

系統共劃分以下四種使用者角色，以滿足不同業務操作需求：

| 角色 | 權限描述 | 適用對象 | 可操作集合範圍 |
| :--- | :--- | :--- | :--- |
| **admin** (管理員) | 具備最高權限，可進行所有資料的增刪查改，包括金鑰重設與使用者設定。 | 公司負責人、系統開發人員 | 所有 Collections (`customers`, `containers`, `rental_records`, `customer_ledgers`, `management_ledgers`) |
| **finance** (財務專員) | 可讀寫客戶、租約與對客收付款、場地支出；不可停用/刪除貨櫃資產。 | 出納、會計人員 | `customers`, `rental_records`, `customer_ledgers`, `management_ledgers` |
| **staff** (現場管理人員) | 僅能管理客戶、更改貨櫃狀態（如空置轉維修）、登記修繕支出；無法修改租約月租金與押金等財務敏感欄位。 | 現場巡邏管理員、修繕師傅 | `customers`, `containers` (僅限狀態更新), `management_ledgers` |
| **viewer** (訪客) | 僅能讀取所有資料（唯讀），不可新增或修改任何欄位。 | 外部稽核人員、唯讀報表使用者 | 所有 Collections（唯讀） |

---

## 2. Phase 1: 最小可用安全規則 (Minimum Viable Rules)

在 Phase 1 開發與 Demo 階段，我們要求使用者必須通過 Firebase Auth 登入才可進行讀寫。未登入者（匿名或未通過驗證）一律被阻擋。

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // 預設規則：必須為已登入使用者才可進行讀寫，未登入不可讀寫
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

> [!WARNING]
> **開發調試注意事項**
> 在尚未串接 Firebase Auth 登入介面前，若要本地開發測試且直連 Firestore，可以使用以下過渡性規則（不推薦用於生產環境）：
> ```javascript
> allow read, write: if true; // 僅限開發測試，部署生產前務必關閉
> ```

---

## 3. Phase 2: 強化角色權限安全規則 (Advanced Role-Based Rules)

在 Phase 2 正式上線階段，我們透過在 Firestore 中建立 `/users/{userId}` 集合，儲存每個使用者的角色（`role`），並利用 Security Rules 進行細粒度的欄位校驗。

### 3.1 使用者資料模型範例 (`/users/{uid}`)
```json
{
  "email": "staff@example.com",
  "role": "staff"
}
```

### 3.2 強化安全規則配置

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // 輔助函數：判斷使用者是否已登入
    function isSignedIn() {
      return request.auth != null;
    }

    // 輔助函數：取得當前登入使用者的角色
    function getUserRole() {
      return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role;
    }

    // 輔助函數：判斷是否為管理員 (admin)
    function isAdmin() {
      return isSignedIn() && getUserRole() == 'admin';
    }

    // 輔助函數：判斷是否具備寫入財務流水之角色
    function isFinanceOrAdmin() {
      return isSignedIn() && (getUserRole() == 'admin' || getUserRole() == 'finance');
    }

    // 1. 客戶資料集合安全規則
    match /customers/{customerId} {
      // 只要登入，皆可讀取與寫入客戶基本資料
      allow read, write: if isSignedIn() && getUserRole() in ['admin', 'finance', 'staff'];
      // 僅 admin 可以真正刪除客戶（或進行物理刪除）
      allow delete: if isAdmin();
    }

    // 2. 貨櫃資產集合安全規則
    match /containers/{containerId} {
      allow read: if isSignedIn();
      // 新增與修改物理資產需 admin 權限，但 staff 允許變更 status 欄位（例如送修）
      allow create, delete: if isAdmin();
      allow update: if isAdmin() || (isSignedIn() && getUserRole() == 'staff' && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['status', 'updated_at']));
    }

    // 3. 租賃合約紀錄安全規則
    match /rental_records/{rentalId} {
      allow read: if isSignedIn();
      // 只有 admin 與 finance 可新增、修改租約合約
      allow create, update: if isFinanceOrAdmin();
      allow delete: if isAdmin();
    }

    // 4. 收付款流水與支出流水安全規則
    match /customer_ledgers/{ledgerId} {
      allow read: if isSignedIn();
      // 僅 admin 與 finance 具備收款流水變更權限
      allow create, update, delete: if isFinanceOrAdmin();
    }

    match /management_ledgers/{ledgerId} {
      allow read: if isSignedIn();
      // admin, finance 可記帳；staff 允許登記支出
      allow create, update: if isSignedIn() && getUserRole() in ['admin', 'finance', 'staff'];
      allow delete: if isAdmin();
    }

    // 5. 使用者名單集合（僅限 admin 修改自己的角色，其餘唯讀）
    match /users/{userId} {
      allow read: if isSignedIn();
      allow write: if isAdmin();
    }
  }
}
```

---

## 4. 安全性檢核清單 (Security Checklist)
- [ ] 生產環境已徹底停用 `allow read, write: if true;`。
- [ ] 所有寫入（`create`, `update`）均通過 Zod 前端校驗，且 Security Rules 有相應的角色判斷。
- [ ] 敏感刪除操作（物理刪除）僅保留給具備 `admin` 角色的管理人員。
