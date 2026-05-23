"use client";

import { useEffect } from "react";
import { PlayCircle, X } from "lucide-react";

interface VideoModalProps {
  onClose: () => void;
}

export default function VideoModal({ onClose }: VideoModalProps) {
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-surface rounded-2xl p-8 max-w-lg w-full text-center relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-text-muted hover:text-text-primary transition-colors"
          aria-label="Close"
        >
          <X size={20} />
        </button>
        <PlayCircle size={48} className="text-brand-blue mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-text-primary mb-2">Demo coming soon</h3>
        <p className="text-text-secondary text-sm mb-6">Check back after launch for a full walkthrough of Journey AI.</p>
        <button
          onClick={onClose}
          className="px-6 py-2.5 bg-muted text-text-primary text-sm font-medium rounded-xl hover:bg-border transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}
