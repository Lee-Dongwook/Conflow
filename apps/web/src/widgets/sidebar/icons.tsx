import { cn } from "@conflow/ui";

export type SidebarGlyph =
  | "dashboard"
  | "mail"
  | "chat"
  | "calendar"
  | "folder"
  | "clipboard"
  | "drive"
  | "megaphone"
  | "clock"
  | "sparkles"
  | "bell"
  | "plus"
  | "settings"
  | "chevronDown"
  | "board"
  | "list"
  | "chart"
  | "huddle"
  | "users"
  | "wrench";

type IconProps = {
  readonly name: SidebarGlyph;
  readonly className?: string;
};

/** Thin outline icons — decorative only; pair with visible labels. */
export const SidebarIcon = ({ name, className }: IconProps) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.75}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden
    className={cn("size-5 shrink-0", className)}
  >
    <Glyph name={name} />
  </svg>
);

const Glyph = ({ name }: { readonly name: SidebarGlyph }) => {
  switch (name) {
    case "dashboard":
      return (
        <>
          <path d="M4 5h7v7H4zM13 5h7v7h-7zM4 14h7v7H4zM13 14h7v7h-7z" />
        </>
      );
    case "mail":
      return (
        <>
          <path d="M4 7h16v10H4z" />
          <path d="m4 7 8 5 8-5" />
        </>
      );
    case "chat":
      return (
        <>
          <path d="M6 8h12v8H9l-3 3v-3H6z" />
          <path d="M9 12h6" />
        </>
      );
    case "calendar":
      return (
        <>
          <path d="M7 4v3M17 4v3" />
          <path d="M5 9h14v11H5z" />
          <path d="M9 13h2v2H9z" />
        </>
      );
    case "folder":
      return <path d="M4 8h6l2 2h10v10H4z" />;
    case "clipboard":
      return (
        <>
          <path d="M9 4h6v2h4v14H6V6h3z" />
          <path d="M9 4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2H9z" />
        </>
      );
    case "drive":
      return <path d="M4 15 7 9h10l3 6H4zm3-6 2-3h6l2 3" />;
    case "megaphone":
      return (
        <>
          <path d="M5 10v4l10 3V7z" />
          <path d="M15 9v6l3 1V8z" />
        </>
      );
    case "clock":
      return (
        <>
          <circle cx="12" cy="12" r="8" />
          <path d="M12 8v4l3 2" />
        </>
      );
    case "sparkles":
      return (
        <>
          <path d="M12 3v3M12 18v3M3 12h3M18 12h3" />
          <path d="m5 5 2 2m10 10 2 2m0-14 2 2M5 19l2-2" />
        </>
      );
    case "bell":
      return (
        <path d="M12 5a4 4 0 0 0-4 4v4l-2 3h12l-2-3V9a4 4 0 0 0-4-4zm0 14a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2z" />
      );
    case "plus":
      return <path d="M12 5v14M5 12h14" />;
    case "settings":
      return (
        <>
          <circle cx="12" cy="12" r="3" />
          <path d="M12 2v2m0 18v2M2 12h2m18 0h2m-3.6-7.4L17 7m-10 10-1.4 1.4M7 7 5.6 5.6m12.8 12.8L17 17M7 17l-1.4 1.4m12.8-12.8L17 7" />
        </>
      );
    case "chevronDown":
      return <path d="m7 10 5 5 5-5" />;
    case "board":
      return (
        <>
          <path d="M5 5h4v14H5zM10 5h4v9h-4zM15 5h4v12h-4z" />
        </>
      );
    case "list":
      return (
        <>
          <path d="M10 8h10M10 12h10M10 16h10" />
          <path
            d="M6 8h.01M6 12h.01M6 16h.01"
            strokeLinecap="round"
            strokeWidth={3}
          />
        </>
      );
    case "chart":
      return (
        <>
          <path d="M4 20h16" />
          <polyline points="6 16 10 9 14 13 18 5 21 10" fill="none" />
        </>
      );
    case "huddle":
      return (
        <>
          <path d="M12 3a7 7 0 0 0-7 7v3a2 2 0 0 0 2 2h1" />
          <path d="M12 3a7 7 0 0 1 7 7v3a2 2 0 0 1-2 2h-1" />
          <path d="M9 18v2a3 3 0 0 0 6 0v-2" />
          <path d="M8 15h8" />
        </>
      );
    case "users":
      return (
        <>
          <circle cx="9" cy="8" r="3" />
          <path d="M4 19v-1a5 5 0 0 1 10 0v1" />
          <path d="M16 6a3 3 0 0 1 0 6m4 7v-1a5 5 0 0 0-3-4.6" />
        </>
      );
    case "wrench":
      return (
        <path d="M15 4a4 4 0 0 0-3.9 5l-5.6 5.6a2 2 0 1 0 2.8 2.8L14 11.9A4 4 0 1 0 15 4z" />
      );
    default:
      return null;
  }
};
