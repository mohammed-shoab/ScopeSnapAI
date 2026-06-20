import http from "k6/http";
import { check, sleep } from "k6";

// k6 load script for the snapai-full-audit skill (full mode only).
// Override target/intensity with env: AUDIT_BASE_URL, VUS, DURATION.
//   k6 run --vus 50 --duration 5m audit/loadtest.js
const BASE = __ENV.AUDIT_BASE_URL || "https://staging.snapai.mainnov.tech";

export const options = {
  vus: Number(__ENV.VUS) || 50,
  duration: __ENV.DURATION || "1m",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<2000"],
  },
};

export default function () {
  const res = http.get(`${BASE}/api/health`);
  check(res, {
    "status is 200": (r) => r.status === 200,
    "body reports ok": (r) => String(r.body).includes("ok"),
  });
  sleep(1);
}
