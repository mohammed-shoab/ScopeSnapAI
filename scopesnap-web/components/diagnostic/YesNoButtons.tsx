"use client";

import { useLang } from "@/lib/language-context";

interface YesNoButtonsProps {
  onAnswer: (value: "yes" | "no") => void;
  disabled?: boolean;
}

export default function YesNoButtons({ onAnswer, disabled = false }: YesNoButtonsProps) {
  const { t } = useLang();
  return (
    <div className="flex gap-4 w-full">
      <button
        onClick={() => onAnswer("yes")}
        disabled={disabled}
        className="flex-1 py-5 rounded-2xl text-white font-extrabold text-xl tracking-wide transition-all active:scale-95 disabled:opacity-50"
        style={{ background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)", boxShadow: "0 4px 14px rgba(26,135,84,.35)" }}
      >
        {t("YES")}
      </button>
      <button
        onClick={() => onAnswer("no")}
        disabled={disabled}
        className="flex-1 py-5 rounded-2xl text-white font-extrabold text-xl tracking-wide transition-all active:scale-95 disabled:opacity-50"
        style={{ background: "linear-gradient(135deg, #c0392b 0%, #e74c3c 100%)", boxShadow: "0 4px 14px rgba(231,76,60,.35)" }}
      >
        {t("NO")}
      </button>
    </div>
  );
}
