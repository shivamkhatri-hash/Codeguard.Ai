import Editor from "react-simple-code-editor";
import Prism from "prismjs";
import "prismjs/components/prism-python";
import "prismjs/components/prism-java";
import "prismjs/components/prism-javascript";
import "prismjs/components/prism-typescript";
import "prismjs/components/prism-c";
import "prismjs/components/prism-cpp";
import "prismjs/components/prism-go";
import "prismjs/components/prism-markup";

const FILE_NAMES = {
  python: "main.py",
  java: "Main.java",
  javascript: "app.js",
  typescript: "app.ts",
  cpp: "main.cpp",
  go: "main.go",
  html: "index.html"
};

function highlightCode(code, language) {
  const langKey = language === "html" ? "markup" : language;
  const grammar = Prism.languages[langKey] || Prism.languages.markup || Prism.languages.javascript;
  try {
    return Prism.highlight(code || " ", grammar, langKey);
  } catch {
    return (code || " ").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

export default function CodeEditor({ code = "", language, fileName, onChange, disabled }) {
  const safeCode = code || "";
  const currentLang = language || "python";
  const displayFile = fileName || FILE_NAMES[currentLang] || "source_code.txt";

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-700/80 bg-[#07101c] shadow-2xl">
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/70 px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
          <span className="ml-2 font-mono text-xs text-slate-400">
            {displayFile}
          </span>
        </div>
        <span className="rounded-md bg-slate-800/70 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          {currentLang}
        </span>
      </div>

      <div className="flex min-h-[430px] overflow-auto">
        <div className="select-none border-r border-slate-800/80 bg-slate-950/40 px-4 py-5 text-right font-mono text-xs leading-6 text-slate-600">
          {Array.from({ length: Math.max(safeCode.split("\n").length, 1) }, (_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>

        <div className="code-editor min-w-0 flex-1 font-mono text-[13px] leading-6">
          <Editor
            value={safeCode}
            onValueChange={onChange}
            highlight={(value) => highlightCode(value, currentLang)}
            padding={20}
            disabled={disabled}
            textareaClassName="min-h-[390px] w-full resize-none"
            preClassName="min-h-[390px]"
            style={{
              minHeight: 430,
              background: "transparent",
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: 13,
              lineHeight: 1.5,
              tabSize: 4
            }}
          />
        </div>
      </div>
    </div>
  );
}