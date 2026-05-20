"use client";
/**
 * /assessments/new — New Assessment entry point (Track DX.2)
 * Redirects to /assess, which is the canonical Step Zero + diagnostic wizard.
 * URL: /assessments/new
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AssessmentsNewPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/assess");
  }, [router]);

  return (
    <div style={{ maxWidth: 480, margin: "64px auto", padding: "0 16px", textAlign: "center", color: "#64748b", fontSize: 14 }}>
      Starting new assessment...
    </div>
  );
}
