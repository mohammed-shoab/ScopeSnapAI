"use client";

export interface VisualOption {
  value: string;
  label: string;
  icon?: string;
}

interface VisualSelectProps {
  options: VisualOption[];
  onAnswer: (value: string) => void;
  disabled?: boolean;
}

export default function VisualSelect({ options, onAnswer, disabled = false }: VisualSelectProps) {
  return (
    <div className="flex flex-col gap-3 w-full">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onAnswer(opt.value)}
          disabled={disabled}
          className="w-full flex items-center gap-4 px-5 py-4 rounded-2xl text-left font-bold text-base transition-all active:scale-95 disabled:opacity-50 border-2"
          style={{
            background: "#16213e",
            borderColor: "#2a2a4a",
            color: "#f0f0f0",
          }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.borderColor = "#3498db"; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.borderColor = "#2a2a4a"; }}
        >
          {opt.icon && <span className="text-2xl flex-shrink-0">{opt.icon}</span>}
          <span>{opt.label}</span>
        </button>
      ))}
    </div>
  );
}
