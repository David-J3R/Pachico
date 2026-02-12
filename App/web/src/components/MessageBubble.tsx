import { Message } from "@/lib/types";
import MarkdownRenderer from "./MarkdownRenderer";
import FileAttachment from "./FileAttachment";

const FILE_PATTERN = /exports[\\/][\w-]+\.(?:png|csv)/g;

function stripFilePaths(text: string): string {
  return text.replace(FILE_PATTERN, "").trim();
}

export default function MessageBubble({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[80%] rounded-2xl bg-bg-user-message px-4 py-3 text-sm leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  const displayText = stripFilePaths(message.content);

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] text-sm leading-relaxed">
        {displayText && <MarkdownRenderer content={displayText} />}
        {message.filePaths.map((fp) => (
          <FileAttachment key={fp} filePath={fp} />
        ))}
      </div>
    </div>
  );
}
