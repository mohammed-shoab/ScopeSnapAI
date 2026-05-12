/**
 * modelCache.ts — Board Session 8, Section 5A
 *
 * IndexedDB-backed cache for equipment model data.
 * Fetches from /api/models/all on first use and caches for 24 hours.
 * Falls back gracefully if IndexedDB is unavailable (SSR, private browsing).
 *
 * Usage:
 *   const brands = await getBrands();
 *   const models = await searchModels("Carrier", "24V");
 */

import { API_URL } from "@/lib/api";

const DB_NAME    = "snapai_models";
const DB_VERSION = 1;
const STORE_META = "meta";
const STORE_MODELS = "models";
const TTL_MS     = 24 * 60 * 60 * 1000; // 24 hours

export interface EquipmentModelRecord {
  id: string;
  brand: string;
  model_series: string;
  equipment_type: string;
  seer_rating: number | null;
  tonnage_range: string | null;
  manufacture_years: string | null;
  avg_lifespan_years: number | null;
  known_issues: Array<{
    component: string;
    issue: string;
    onset_year?: number;
    frequency?: string;
    regions?: string[];
  }>;
  replacement_models: string[];
}

// ── In-memory fallback (when IndexedDB isn't available) ───────────────────────
let _memoryCache: EquipmentModelRecord[] | null = null;
let _memoryCacheTime = 0;

// ── IndexedDB helpers ─────────────────────────────────────────────────────────

function openDB(): Promise<IDBDatabase | null> {
  if (typeof window === "undefined" || !window.indexedDB) return Promise.resolve(null);

  return new Promise((resolve) => {
    try {
      const req = indexedDB.open(DB_NAME, DB_VERSION);

      req.onupgradeneeded = (e) => {
        const db = (e.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(STORE_MODELS)) {
          const store = db.createObjectStore(STORE_MODELS, { keyPath: "id" });
          store.createIndex("brand", "brand", { unique: false });
          store.createIndex("model_series", "model_series", { unique: false });
        }
        if (!db.objectStoreNames.contains(STORE_META)) {
          db.createObjectStore(STORE_META);
        }
      };

      req.onsuccess = (e) => resolve((e.target as IDBOpenDBRequest).result);
      req.onerror   = () => resolve(null); // Degrade gracefully
    } catch {
      resolve(null);
    }
  });
}

function idbGet<T>(db: IDBDatabase, store: string, key: string): Promise<T | undefined> {
  return new Promise((resolve) => {
    try {
      const tx  = db.transaction(store, "readonly");
      const req = tx.objectStore(store).get(key);
      req.onsuccess = () => resolve(req.result as T | undefined);
      req.onerror   = () => resolve(undefined);
    } catch {
      resolve(undefined);
    }
  });
}

function idbPut(db: IDBDatabase, store: string, value: unknown, key?: string): Promise<void> {
  return new Promise((resolve) => {
    try {
      const tx  = db.transaction(store, "readwrite");
      const s   = tx.objectStore(store);
      const req = key ? s.put(value, key) : s.put(value);
      req.onsuccess = () => resolve();
      req.onerror   = () => resolve();
    } catch {
      resolve();
    }
  });
}

function idbGetAll(db: IDBDatabase, store: string): Promise<EquipmentModelRecord[]> {
  return new Promise((resolve) => {
    try {
      const tx  = db.transaction(store, "readonly");
      const req = tx.objectStore(store).getAll();
      req.onsuccess = () => resolve((req.result as EquipmentModelRecord[]) || []);
      req.onerror   = () => resolve([]);
    } catch {
      resolve([]);
    }
  });
}

function idbClear(db: IDBDatabase, store: string): Promise<void> {
  return new Promise((resolve) => {
    try {
      const tx  = db.transaction(store, "readwrite");
      const req = tx.objectStore(store).clear();
      req.onsuccess = () => resolve();
      req.onerror   = () => resolve();
    } catch {
      resolve();
    }
  });
}

// ── Fetch + populate cache ────────────────────────────────────────────────────

async function fetchAndCache(): Promise<EquipmentModelRecord[]> {
  const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";

  const headers: Record<string, string> = {};
  if (IS_DEV) headers["X-Dev-Clerk-User-Id"] = "test_user_mike";

  let models: EquipmentModelRecord[] = [];

  try {
    const res = await fetch(`${API_URL}/api/models/all`, {
      headers,
      // No auth needed — public reference data
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    models = data.models || [];
  } catch (err) {
    console.warn("[modelCache] fetch failed:", err);
    return _memoryCache || [];
  }

  // Store in memory fallback
  _memoryCache     = models;
  _memoryCacheTime = Date.now();

  // Store in IndexedDB
  const db = await openDB();
  if (db) {
    await idbClear(db, STORE_MODELS);
    for (const m of models) {
      await idbPut(db, STORE_MODELS, m);
    }
    await idbPut(db, STORE_META, Date.now(), "cached_at");
    db.close();
  }

  return models;
}

// ── Public API ────────────────────────────────────────────────────────────────

/** Ensure the local cache is populated (fetch if expired or empty). */
async function ensureLoaded(): Promise<EquipmentModelRecord[]> {
  // 1. Check memory cache first (fastest)
  if (_memoryCache && Date.now() - _memoryCacheTime < TTL_MS) {
    return _memoryCache;
  }

  // 2. Check IndexedDB
  const db = await openDB();
  if (db) {
    const cachedAt = await idbGet<number>(db, STORE_META, "cached_at");
    if (cachedAt && Date.now() - cachedAt < TTL_MS) {
      const models = await idbGetAll(db, STORE_MODELS);
      db.close();
      if (models.length > 0) {
        _memoryCache     = models;
        _memoryCacheTime = Date.now();
        return models;
      }
    }
    db.close();
  }

  // 3. Cache expired or empty — fetch from API
  return fetchAndCache();
}

/**
 * Returns distinct brands with model counts.
 * Computed from local cache — no network call after first load.
 */
export async function getBrands(): Promise<Array<{ brand: string; model_count: number }>> {
  const models = await ensureLoaded();
  const counts = new Map<string, number>();
  for (const m of models) {
    counts.set(m.brand, (counts.get(m.brand) || 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([brand, model_count]) => ({ brand, model_count }))
    .sort((a, b) => b.model_count - a.model_count || a.brand.localeCompare(b.brand));
}

/**
 * Search models by brand and/or prefix.
 *
 * @param brand  - Exact brand name (case-insensitive). Pass "" for all brands.
 * @param q      - Model series prefix (case-insensitive). Pass "" for no filter.
 * @param equipmentType - Optional equipment type filter.
 * @param limit  - Max results to return (default 20).
 */
export async function searchModels(
  brand: string,
  q: string,
  equipmentType?: string,
  limit = 20,
): Promise<EquipmentModelRecord[]> {
  const models = await ensureLoaded();

  const brandLower  = brand.trim().toLowerCase();
  const qLower      = q.trim().toLowerCase();

  return models
    .filter((m) => {
      if (brandLower && m.brand.toLowerCase() !== brandLower) return false;
      if (qLower && !m.model_series.toLowerCase().includes(qLower)) return false;
      if (equipmentType && m.equipment_type !== equipmentType) return false;
      return true;
    })
    .slice(0, limit);
}

/**
 * Force-refresh the cache from the API.
 * Call this if the user reports stale data.
 */
export async function refreshModelCache(): Promise<void> {
  _memoryCache     = null;
  _memoryCacheTime = 0;
  await fetchAndCache();
}

/**
 * Preload the model cache in the background (call on app init).
 * Silent — does not throw.
 */
export function preloadModelCache(): void {
  if (typeof window === "undefined") return;
  // Delay 3s so it doesn't compete with critical path
  setTimeout(() => {
    ensureLoaded().catch(() => {/* ignore */});
  }, 3000);
}
