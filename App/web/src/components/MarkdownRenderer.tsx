import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

const components: Components = {
  p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="mb-3 ml-6 list-disc space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="mb-3 ml-6 list-decimal space-y-1">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  h1: ({ children }) => <h1 className="mb-3 text-xl font-bold">{children}</h1>,
  h2: ({ children }) => <h2 className="mb-2 text-lg font-bold">{children}</h2>,
  h3: ({ children }) => <h3 className="mb-2 text-base font-semibold">{children}</h3>,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-accent-primary hover:text-accent-hover underline"
    >
      {children}
    </a>
  ),
  code: ({ className, children }) => {
    const isBlock = className?.includes("language-");
    if (isBlock) {
      return (
        <pre className="mb-3 overflow-x-auto rounded-lg bg-bg-sidebar p-4 text-sm">
          <code className={className}>{children}</code>
        </pre>
      );
    }
    return (
      <code className="rounded bg-bg-tertiary px-1.5 py-0.5 text-sm">{children}</code>
    );
  },
  pre: ({ children }) => <>{children}</>,
  table: ({ children }) => (
    <div className="mb-3 overflow-x-auto rounded-lg border border-border-primary">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-bg-tertiary text-text-secondary">{children}</thead>
  ),
  tbody: ({ children }) => <tbody>{children}</tbody>,
  tr: ({ children }) => (
    <tr className="border-b border-border-primary last:border-0">{children}</tr>
  ),
  th: ({ children }) => (
    <th className="px-3 py-2 text-left font-semibold">{children}</th>
  ),
  td: ({ children }) => <td className="px-3 py-2">{children}</td>,
  blockquote: ({ children }) => (
    <blockquote className="mb-3 border-l-3 border-accent-primary pl-4 text-text-secondary italic">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-4 border-border-primary" />,
};

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  );
}
