import { Code2 } from "lucide-react";

const LANGUAGES = [
  { value: "python", label: "Python", mark: "Py" },
  { value: "java", label: "Java", mark: "Ja" },
  { value: "javascript", label: "JavaScript", mark: "JS" },
  { value: "typescript", label: "TypeScript", mark: "TS" },
  { value: "cpp", label: "C++", mark: "C++" },
  { value: "go", label: "Go", mark: "Go" },
  { value: "html", label: "HTML", mark: "HT" },
];

export default function LanguageSelector({ language, onChange }) {
  return (
    <div>
      <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-300">
        <Code2 size={16} className="text-cyan-300" />
        Language
      </label>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-2">
        {LANGUAGES.map((item) => (
          <button
            key={item.value}
            type="button"
            onClick={() => onChange(item.value)}
            className={`flex items-center gap-2.5 rounded-xl border px-2.5 py-2 text-left transition ${
              language === item.value
                ? "border-cyan-400/50 bg-cyan-400/10 text-white shadow-glow"
                : "border-slate-700/70 bg-slate-950/50 text-slate-400 hover:border-slate-600 hover:text-slate-200"
            }`}
          >
            <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-lg text-[11px] font-bold ${
              language === item.value ? "bg-cyan-400 text-slate-950" : "bg-slate-800 text-slate-300"
            }`}>
              {item.mark}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-xs font-semibold">{item.label}</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}