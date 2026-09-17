import { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Bot, User, Sparkles, X, BookOpen, Trash2, ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import { sendChatMessage } from "../services/api";

const SUGGESTED_PROMPTS = [
  "How can I prevent SQL injection in my code?",
  "Explain why hardcoded secrets are dangerous.",
  "What is the best way to prevent Cross-Site Scripting (XSS)?",
  "How can I reduce cyclomatic complexity in large functions?",
];

function parseInlineMarkdown(text) {
  if (!text) return null;
  const parts = text.split(/(\*\*[\s\S]+?\*\*|`[^`]+`|\*[^\*]+\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
      return (
        <strong key={i} className="font-semibold text-slate-100">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
      return (
        <code key={i} className="rounded bg-slate-800/80 px-1.5 py-0.5 font-mono text-[11px] text-cyan-300 border border-slate-700/60">
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith("*") && part.endsWith("*") && part.length >= 2 && !part.startsWith("**")) {
      return (
        <em key={i} className="italic text-slate-300">
          {part.slice(1, -1)}
        </em>
      );
    }
    return part;
  });
}

function FormattedText({ text }) {
  if (!text) return null;
  const lines = text.split("\n");
  return (
    <div className="space-y-1">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={idx} className="h-1.5" />;
        }

        if (trimmed.startsWith("### ")) {
          return (
            <h3 key={idx} className="font-bold text-sm text-cyan-300 mt-2 mb-1">
              {parseInlineMarkdown(trimmed.slice(4))}
            </h3>
          );
        }
        if (trimmed.startsWith("#### ")) {
          return (
            <h4 key={idx} className="font-semibold text-xs text-indigo-300 mt-1.5 mb-0.5">
              {parseInlineMarkdown(trimmed.slice(5))}
            </h4>
          );
        }

        if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
          return (
            <div key={idx} className="flex gap-2 pl-2 text-slate-200">
              <span className="text-cyan-400 font-bold select-none">•</span>
              <span>{parseInlineMarkdown(trimmed.slice(2))}</span>
            </div>
          );
        }

        const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
        if (numMatch) {
          return (
            <div key={idx} className="flex gap-2 pl-2 text-slate-200">
              <span className="text-cyan-400 font-bold select-none">{numMatch[1]}.</span>
              <span>{parseInlineMarkdown(numMatch[2])}</span>
            </div>
          );
        }

        return (
          <p key={idx} className="text-slate-200 leading-relaxed">
            {parseInlineMarkdown(line)}
          </p>
        );
      })}
    </div>
  );
}

function MessageContent({ content }) {
  const [copiedCode, setCopiedCode] = useState(null);

  if (!content) return null;

  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-2 font-sans text-xs leading-relaxed">
      {parts.map((part, index) => {
        if (part.startsWith("```") && part.endsWith("```")) {
          const firstLineEnd = part.indexOf("\n");
          let codeLang = "code";
          let codeText = part.slice(3, -3);
          if (firstLineEnd !== -1 && firstLineEnd < 20) {
            codeLang = part.slice(3, firstLineEnd).trim() || "code";
            codeText = part.slice(firstLineEnd + 1, -3);
          }
          const isCopied = copiedCode === index;

          return (
            <div key={index} className="my-2 overflow-hidden rounded-xl border border-slate-700/80 bg-slate-950/90 shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/80 px-3 py-1.5 font-mono text-[10px] text-slate-400">
                <span className="uppercase text-cyan-400 font-bold">{codeLang}</span>
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(codeText.trim());
                    setCopiedCode(index);
                    setTimeout(() => setCopiedCode(null), 2000);
                  }}
                  className="inline-flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-[10px] font-bold text-slate-200 hover:bg-slate-700 transition"
                >
                  {isCopied ? <Check size={11} className="text-emerald-300" /> : <Copy size={11} />}
                  <span>{isCopied ? "Copied!" : "Copy"}</span>
                </button>
              </div>
              <pre className="overflow-x-auto p-3 font-mono text-[11px] text-slate-200 leading-relaxed">
                <code>{codeText.trim()}</code>
              </pre>
            </div>
          );
        }

        return <FormattedText key={index} text={part} />;
      })}
    </div>
  );
}

export default function ConversationalAssistant({ analysisId, language = "python", isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am your **CodeGuard AI Assistant**, grounded in our Secure Coding Knowledge Base. Ask me follow-up questions about flagged vulnerabilities, refactoring advice, or secure coding guidelines!",
      sources: [],
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const text = queryText || inputQuery;
    if (!text.trim() || loading) return;

    const userMsg = { role: "user", content: text };
    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setInputQuery("");
    setLoading(true);

    try {
      const historyPayload = newHistory.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await sendChatMessage({
        query: text,
        analysisId: analysisId !== "—" ? analysisId : null,
        language,
        history: historyPayload,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.response || "No response received.",
          sources: res.sources || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠️ Failed to get a response: ${err.message || "An unexpected error occurred."}`,
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: "assistant",
        content: "Chat cleared. Feel free to ask any question regarding code quality or security vulnerabilities!",
        sources: [],
      },
    ]);
  };

  const toggleSourceView = (idx) => {
    setShowSources((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  if (!isOpen) return null;

  return (
    <div
      id="assistant-drawer"
      role="region"
      aria-label="Conversational Code Assistant"
      className="fixed inset-y-0 right-0 z-50 flex w-full max-w-lg flex-col border-l border-slate-700/80 bg-[#080e1a]/95 backdrop-blur-xl shadow-2xl transition-all duration-300 max-w-full sm:max-w-lg overflow-x-hidden"
    >
      {/* Drawer Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 px-5 py-4 bg-slate-900/60">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-tr from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-400/30">
            <Bot size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-100">Conversational Code Assistant</h3>
              <span className="rounded bg-cyan-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-cyan-300 border border-cyan-500/20">
                RAG Grounded
              </span>
            </div>
            <p className="text-xs text-slate-400">Context: {language ? language.toUpperCase() : "Python"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleClear}
            title="Clear Chat"
            aria-label="Clear chat messages"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
          >
            <Trash2 size={16} />
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close Assistant drawer"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Messages Thread */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            <div
              className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${
                msg.role === "user"
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                  : "bg-slate-800 text-indigo-300 border border-slate-700"
              }`}
            >
              {msg.role === "user" ? <User size={15} /> : <Sparkles size={15} />}
            </div>

            <div className={`max-w-[85%] space-y-2`}>
              <div
                className={`rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                  msg.role === "user"
                    ? "bg-cyan-600/20 text-cyan-100 border border-cyan-500/30 rounded-tr-none"
                    : "bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none"
                }`}
              >
                <MessageContent content={msg.content} />
              </div>

              {/* RAG Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-2.5">
                  <button
                    type="button"
                    onClick={() => toggleSourceView(idx)}
                    aria-label="Toggle RAG citations view"
                    className="flex w-full items-center justify-between text-[11px] font-semibold text-slate-400 hover:text-cyan-300"
                  >
                    <span className="flex items-center gap-1.5">
                      <BookOpen size={12} className="text-cyan-400" />
                      {msg.sources.length} RAG Knowledge Base Citation(s)
                    </span>
                    {showSources[idx] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>

                  {showSources[idx] && (
                    <div className="mt-2 space-y-1.5 pt-2 border-t border-slate-800">
                      {msg.sources.map((src, sIdx) => (
                        <div key={sIdx} className="rounded bg-slate-900 p-2 text-[10px]">
                          <div className="flex items-center justify-between font-bold text-cyan-300">
                            <span>{src.title}</span>
                            <span className="text-slate-500">{src.category}</span>
                          </div>
                          <p className="mt-1 text-slate-400 line-clamp-2">{src.snippet}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-slate-800 text-indigo-300 border border-slate-700">
              <Sparkles size={15} className="animate-spin" />
            </div>
            <div className="rounded-2xl rounded-tl-none bg-slate-900 px-4 py-2.5 text-xs text-slate-400 border border-slate-800">
              Consulting RAG Knowledge Base & generating answer...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      <div className="border-t border-slate-800/80 bg-slate-900/30 px-4 py-2 max-w-full overflow-hidden">
        <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">Suggested Questions</p>
        <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none max-w-full flex-nowrap">
          {(analysisId && analysisId !== "—" ? [
            "What are all findings in this file?",
            "How do I fix high severity issues?",
            "Explain OWASP Top 10 vulnerabilities",
            "How do I prevent SQL injection?"
          ] : SUGGESTED_PROMPTS).map((prompt, pIdx) => (
            <button
              key={pIdx}
              type="button"
              onClick={() => handleSend(prompt)}
              aria-label={`Ask suggested question: ${prompt}`}
              className="shrink-0 rounded-lg border border-slate-700/60 bg-slate-800/40 px-2.5 py-1 text-[11px] text-slate-300 hover:border-cyan-400/40 hover:bg-cyan-500/10 hover:text-cyan-200 transition"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <div className="border-t border-slate-800 p-4 bg-slate-900/70">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            aria-label="Ask assistant a coding question"
            placeholder="Ask anything about flagged issues, fixes, OWASP rules..."
            className="flex-1 rounded-xl border border-slate-700/80 bg-slate-950 px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || loading}
            aria-label="Send message"
            className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
}
