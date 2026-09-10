import { AlertCircle, CheckCircle2, FileCode2, Upload, X } from "lucide-react";
import { useRef, useState } from "react";

const ACCEPTED = [".py", ".java", ".js", ".ts", ".cpp", ".cc", ".h", ".go", ".html", ".htm"];

const EXT_LANG_MAP = {
  ".py": "python",
  ".java": "java",
  ".js": "javascript",
  ".ts": "typescript",
  ".cpp": "cpp",
  ".cc": "cpp",
  ".h": "cpp",
  ".go": "go",
  ".html": "html",
  ".htm": "html"
};

function extensionOf(name = "") {
  const index = name.lastIndexOf(".");
  return index >= 0 ? name.slice(index).toLowerCase() : "";
}

export default function FileUpload({ onCodeLoaded, onFileNameChange, onLanguageDetected, disabled }) {
  const inputRef = useRef(null);
  const [fileName, setFileName] = useState("");
  const [message, setMessage] = useState("");

  const reset = () => {
    setFileName("");
    setMessage("");
    if (inputRef.current) inputRef.current.value = "";
    onFileNameChange("");
  };

  const handleFile = async (file) => {
    if (!file) return;

    const ext = extensionOf(file.name);
    if (!ACCEPTED.includes(ext)) {
      setMessage("Unsupported file type. Please select a valid code source file.");
      setFileName("");
      onFileNameChange("");
      return;
    }

    try {
      const code = await file.text();
      setFileName(file.name);
      onFileNameChange(file.name);
      const detected = EXT_LANG_MAP[ext] || "python";
      onLanguageDetected(detected);
      onCodeLoaded(code);
      setMessage("File loaded into the editor.");
    } catch {
      setMessage("Could not read this file.");
    }
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".py,.java,.js,.ts,.cpp,.cc,.h,.go,.html,.htm"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
        disabled={disabled}
      />

      <div className="flex items-center justify-between gap-3">
        <button
          type="button"
            disabled={disabled}
          onClick={() => inputRef.current?.click()}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-dashed border-slate-600 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-cyan-400/60 hover:bg-cyan-400/5 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Upload size={17} />
          Upload source file
        </button>

        {fileName && (
          <button
            type="button"
            onClick={reset}
            className="rounded-xl border border-slate-700 bg-slate-900 p-3 text-slate-400 hover:text-white"
            title="Remove file"
          >
            <X size={17} />
          </button>
        )}
      </div>

      {fileName ? (
        <div className="mt-3 flex items-center gap-3 rounded-xl border border-emerald-400/15 bg-emerald-400/5 px-3 py-2.5">
          <FileCode2 size={18} className="text-emerald-300" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-200">{fileName}</p>
            <p className="text-xs text-slate-500">Loaded into editor</p>
          </div>
          <CheckCircle2 size={17} className="text-emerald-300" />
        </div>
      ) : (
        <p className="mt-2 text-xs text-slate-500">Formats: .py, .java, .js, .ts, .cpp, .go, .html</p>
      )}

      {message && !fileName && (
        <p className="mt-2 flex items-center gap-2 text-xs text-rose-300">
          <AlertCircle size={14} /> {message}
        </p>
      )}
      {message && fileName && (
        <p className="mt-2 text-xs text-emerald-300">{message}</p>
      )}
    </div>
  );
}