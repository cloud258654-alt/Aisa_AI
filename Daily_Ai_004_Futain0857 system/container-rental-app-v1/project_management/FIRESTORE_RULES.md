# Firestore Security Rules

生產規則的唯一來源是根目錄 `firestore.rules`，不使用「登入即可全讀寫」或 `allow ... if true` 的過渡規則。

所有請求都必須已登入、存在 `users/{uid}`，且 Profile 的 `status` 為 `active`。角色為 admin、manager、finance、staff：所有角色可讀營運集合；客戶由 admin/manager/staff 寫入；貨櫃由 admin/manager 寫入，staff 僅限非成本與非軟刪除欄位；租約僅 admin/manager 可寫；兩種帳務由 admin/manager/finance 可寫。`deleted_at` 僅 admin/manager 可變更。

`users` 僅本人可讀取自身 Profile，admin 可管理所有 Profile；一般使用者不可改 `uid`、`role`、`status`。首位 admin 要在 Firebase Console 建立，因為 Rules 不允許未授權自我升權。

執行 `npm run test:rules` 會使用 Firestore Emulator 驗證未登入、無 Profile、停用、admin、manager、finance、staff 及自我升權案例。
