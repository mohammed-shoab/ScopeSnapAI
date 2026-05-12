/**
 * SnapAI — Offline Queue (IndexedDB)
 * SOW Task 1.8: Store pending assessment uploads when offline.
 * Auto-syncs when network reconnects.
 *
 * Flow:
 *  1. User is offline while submitting → saveToQueue(photos, metadata)
 *  2. On reconnect → processQueue() uploads all queued items
 *  3. Each item removed from queue after successful upload
 *
 * Storage: IndexedDB DB="snapai_offline" store="pending_assessments"
 * Each entry: { id, photos: File[], metadata, queuedAt }
 */

const DB_NAME    = "snapai_offline";
const DB_VERSION = 1;
const STORE_NAME = "pending_assessments";

export interface PendingAssessment {
  id: string;
  photosData: { name: string; type: string; data: ArrayBuffer }[];
  address: string;
  customerName: string;
  customerPhone: string;
  queuedAt: number;
}

// ── Open DB ───────────────────────────────────────────────────────────────────
function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === "undefined") {
      reject(new Error("IndexedDB not available"));
      return;
    }
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    req.onsuccess = (e) => resolve((e.target as IDBOpenDBRequest).result);
    req.onerror   = (e) => reject((e.target as IDBOpenDBRequest).error);
  });
}

// ── File → ArrayBuffer ────────────────────────────────────────────────────────
async function fileToBuffer(file: File): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target!.result as ArrayBuffer);
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

// ── Save to queue ─────────────────────────────────────────────────────────────
export async function saveToOfflineQueue(
  photos: File[],
  metadata: { address: string; customerName: string; customerPhone: string }
): Promise<string> {
  const db = await openDB();
  const id = `pending-${Date.now()}-${Math.random().toString(36).slice(2)}`;

  const photosData = await Promise.all(
    photos.map(async (f) => ({
      name: f.name,
      type: f.type,
      data: await fileToBuffer(f),
    }))
  );

  const entry: PendingAssessment = {
    id,
    photosData,
    address: metadata.address,
    customerName: metadata.customerName,
    customerPhone: metadata.customerPhone,
    queuedAt: Date.now(),
  };

  await new Promise<void>((resolve, reject) => {
    const tx    = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const req   = store.add(entry);
    req.onsuccess = () => resolve();
    req.onerror   = () => reject(req.error);
  });

  db.close();
  _notifyQueueListeners();
  return id;
}

// ── Get all queued items ──────────────────────────────────────────────────────
export async function getOfflineQueue(): Promise<PendingAssessment[]> {
  const db = await openDB();
  const result = await new Promise<PendingAssessment[]>((resolve, reject) => {
    const tx    = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const req   = store.getAll();
    req.onsuccess = () => resolve(req.result as PendingAssessment[]);
    req.onerror   = () => reject(req.error);
  });
  db.close();
  return result;
}

// ── Remove one item ───────────────────────────────────────────────────────────
export async function removeFromOfflineQueue(id: string): Promise<void> {
  const db = await openDB();
  await new Promise<void>((resolve, reject) => {
    const tx    = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const req   = store.delete(id);
    req.onsuccess = () => resolve();
    req.onerror   = () => reject(req.error);
  });
  db.close();
  _notifyQueueListeners();
}

// ── Count queued items ────────────────────────────────────────────────────────
export async function getOfflineQueueCount(): Promise<number> {
  try {
    const db = await openDB();
    const count = await new Promise<number>((resolve, reject) => {
      const tx    = db.transaction(STORE_NAME, "readonly");
      const store = tx.objectStore(STORE_NAME);
      const req   = store.count();
      req.onsuccess = () => resolve(req.result);
      req.onerror   = () => reject(req.error);
    });
    db.close();
    return count;
  } catch {
    return 0;
  }
}

// ── Process queue (upload all pending items) ──────────────────────────────────
export async function processOfflineQueue(
  apiUrl: string,
  headers: Record<string, string>,
): Promise<void> {
  const items = await getOfflineQueue();
  for (const item of items) {
    try {
      const formData = new FormData();
      formData.append("address", item.address);
      formData.append("customer_name", item.customerName);
      formData.append("customer_phone", item.customerPhone);

      for (const p of item.photosData) {
        const blob = new Blob([p.data], { type: p.type });
        formData.append("photos", blob, p.name);
      }

      const res = await fetch(`${apiUrl}/api/assessments`, {
        method: "POST",
        headers,
        body: formData,
      });

      if (res.ok) {
        await removeFromOfflineQueue(item.id);
      }
    } catch {
      // Leave in queue — will retry on next sync
    }
  }
}

// ── Section 6C additions ──────────────────────────────────────────────────────

/** Returns true when the device has no network */
export function isOffline(): boolean {
  if (typeof window === "undefined") return false;
  return !navigator.onLine;
}

/** Queue-count change listeners — notified after every add/remove */
type QueueCountListener = (count: number) => void;
const _queueListeners: Set<QueueCountListener> = new Set();

function _notifyQueueListeners(): void {
  getOfflineQueueCount()
    .then(count => _queueListeners.forEach(fn => fn(count)))
    .catch(() => {});
}

/**
 * Subscribe to offline queue count changes.
 * Fires immediately with the current count, then on every change.
 * Returns an unsubscribe function.
 */
export function subscribeToQueueCount(fn: QueueCountListener): () => void {
  _queueListeners.add(fn);
  getOfflineQueueCount().then(fn).catch(() => fn(0));
  return () => _queueListeners.delete(fn);
}

/**
 * Wire up automatic sync when the device comes back online.
 * Call once on app init. Returns cleanup function.
 *
 * @param apiUrl     - Backend API base URL
 * @param getHeaders - Function returning auth headers for the current session
 */
export function setupAutoSync(
  apiUrl: string,
  getHeaders: () => Record<string, string>,
): () => void {
  if (typeof window === "undefined") return () => { return; };

  const handler = () => {
    processOfflineQueue(apiUrl, getHeaders()).catch(() => { return; });
  };

  window.addEventListener("online", handler);

  // Sync immediately if already online and there are pending items
  if (navigator.onLine) {
    getOfflineQueueCount().then(count => {
      if (count > 0) handler();
    });
  }

  return () => window.removeEventListener("online", handler);
}
