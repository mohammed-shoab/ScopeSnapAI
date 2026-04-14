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

// ── Process queue: upload all pending assessments ─────────────────────────────
export async function processOfflineQueue(
  apiUrl: string,
  devHeader: Record<string, string>,
  onProgress?: (id: string, done: boolean) => void
): Promise<{ uploaded: number; failed: number }> {
  let uploaded = 0;
  let failed   = 0;

  let items: PendingAssessment[] = [];
  try {
    items = await getOfflineQueue();
  } catch {
    return { uploaded, failed };
  }

  for (const item of items) {
    try {
      const fd = new FormData();
      for (const photoData of item.photosData) {
        const blob = new Blob([photoData.data], { type: photoData.type });
        fd.append("photos", blob, photoData.name);
      }
      if (item.address)      fd.append("property_address", item.address);
      if (item.customerName) fd.append("homeowner_name",   item.customerName);
      if (item.customerPhone) fd.append("homeowner_phone", item.customerPhone);

      const res = await fetch(`${apiUrl}/api/assessments/`, {
        method: "POST",
        headers: devHeader,
        body: fd,
      });

      if (res.ok) {
        await removeFromOfflineQueue(item.id);
        uploaded++;
        onProgress?.(item.id, true);
      } else {
        failed++;
        onProgress?.(item.id, false);
      }
    } catch {
      failed++;
      onProgress?.(item.id, false);
    }
  }

  return { uploaded, failed };
}
