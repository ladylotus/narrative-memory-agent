/* Minimal icon set — primitives only (line / circle / rect). */
function Icon({ name, size = 16, stroke = 1.6 }) {
  const p = {
    width: size, height: size, viewBox: "0 0 24 24", fill: "none",
    stroke: "currentColor", strokeWidth: stroke,
    strokeLinecap: "round", strokeLinejoin: "round",
  };
  switch (name) {
    case "chat": // rounded square speech frame
      return (
        <svg {...p}>
          <rect x="3.5" y="4.5" width="17" height="12" rx="3" />
          <path d="M8 16.5l-1.5 3 4-3" />
        </svg>
      );
    case "profile": // head + shoulders
      return (
        <svg {...p}>
          <circle cx="12" cy="8" r="3.4" />
          <path d="M5.5 19a6.5 6.5 0 0 1 13 0" />
        </svg>
      );
    case "moon": // crescent from two circles (mask)
      return (
        <svg {...p}>
          <path d="M20 14.5A8 8 0 1 1 9.5 4a6.3 6.3 0 0 0 10.5 10.5Z" />
        </svg>
      );
    case "settings": // sliders — lines + circles
      return (
        <svg {...p}>
          <line x1="4" y1="8" x2="20" y2="8" />
          <line x1="4" y1="16" x2="20" y2="16" />
          <circle cx="15" cy="8" r="2.4" fill="var(--bg-sidebar)" />
          <circle cx="9" cy="16" r="2.4" fill="var(--bg-sidebar)" />
        </svg>
      );
    case "book":
      return (
        <svg {...p}>
          <rect x="5" y="4" width="14" height="16" rx="1.5" />
          <line x1="9" y1="4" x2="9" y2="20" />
        </svg>
      );
    case "plus":
      return (
        <svg {...p}>
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
      );
    case "send": // arrow up
      return (
        <svg {...p}>
          <line x1="12" y1="19" x2="12" y2="6" />
          <path d="M6.5 11.5L12 5.5l5.5 6" />
        </svg>
      );
    case "upload":
      return (
        <svg {...p}>
          <path d="M12 15V5" />
          <path d="M7.5 9.5L12 5l4.5 4.5" />
          <path d="M5 16v2.5a1.5 1.5 0 0 0 1.5 1.5h11a1.5 1.5 0 0 0 1.5-1.5V16" />
        </svg>
      );
    case "check":
      return (
        <svg {...p} strokeWidth="2.2">
          <path d="M5 12.5l4 4 10-10" />
        </svg>
      );
    case "refresh":
      return (
        <svg {...p}>
          <path d="M19 12a7 7 0 1 1-2-4.9" />
          <path d="M19 4v3.5h-3.5" />
        </svg>
      );
    case "spark": // 4-point — two crossed lines
      return (
        <svg {...p}>
          <path d="M12 4v16" />
          <path d="M4 12h16" />
          <path d="M7 7l10 10" opacity="0.45" />
          <path d="M17 7L7 17" opacity="0.45" />
        </svg>
      );
    case "arrow":
      return (
        <svg {...p}>
          <line x1="5" y1="12" x2="19" y2="12" />
          <path d="M13 6l6 6-6 6" />
        </svg>
      );
    case "dot":
      return (
        <svg {...p}><circle cx="12" cy="12" r="4" fill="currentColor" stroke="none" /></svg>
      );
    case "flag":
      return (
        <svg {...p}>
          <line x1="6" y1="3.5" x2="6" y2="20.5" />
          <path d="M6 5h11l-2.5 3.5L17 12H6" />
        </svg>
      );
    case "link":
      return (
        <svg {...p}>
          <rect x="3.5" y="9" width="8" height="6" rx="3" />
          <rect x="12.5" y="9" width="8" height="6" rx="3" />
          <line x1="9" y1="12" x2="15" y2="12" />
        </svg>
      );
    default:
      return <svg {...p}><circle cx="12" cy="12" r="7" /></svg>;
  }
}

Object.assign(window, { Icon });
