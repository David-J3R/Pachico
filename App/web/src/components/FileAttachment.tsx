import { getFileUrl } from "@/lib/api";

interface FileAttachmentProps {
  filePath: string;
}

export default function FileAttachment({ filePath }: FileAttachmentProps) {
  const url = getFileUrl(filePath);
  const fileName = filePath.split("/").pop() || filePath;
  const isImage = /\.(png|jpg|jpeg|gif|webp)$/i.test(filePath);

  if (isImage) {
    return (
      <a href={url} target="_blank" rel="noopener noreferrer" className="block my-2">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={url}
          alt={fileName}
          className="max-w-full max-h-96 rounded-lg border border-border-primary cursor-pointer hover:opacity-90 transition-opacity"
        />
      </a>
    );
  }

  return (
    <a
      href={url}
      download
      className="inline-flex items-center gap-2 my-2 px-3 py-2 rounded-lg bg-bg-tertiary border border-border-primary hover:bg-bg-hover transition-colors text-sm"
    >
      <svg
        className="w-4 h-4 text-text-secondary"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <span className="text-text-primary">{fileName}</span>
    </a>
  );
}
