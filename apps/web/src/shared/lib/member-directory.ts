/**
 * member-directory — resolves a member UUID to a human-friendly display
 * identity (name, role, avatar color) for chat / comms UIs.
 *
 * The backend has no member-name resolution endpoint yet, so demo members
 * are mapped explicitly. Unknown UUIDs fall back to a deterministic name +
 * color derived from the UUID, so real workspaces still render reasonably.
 */

export interface MemberIdentity {
  readonly name: string
  readonly role: string
  /** Tailwind classes for the avatar chip (bg + text). */
  readonly avatar: string
}

const AVATAR_PALETTE: readonly string[] = [
  'bg-rose-100 text-rose-700',
  'bg-amber-100 text-amber-700',
  'bg-emerald-100 text-emerald-700',
  'bg-sky-100 text-sky-700',
  'bg-violet-100 text-violet-700',
  'bg-teal-100 text-teal-700',
  'bg-indigo-100 text-indigo-700',
  'bg-fuchsia-100 text-fuchsia-700',
]

const DEMO_MEMBERS: Record<string, MemberIdentity> = {
  'demo-member-you': {
    name: '나',
    role: '데모 방문자',
    avatar: 'bg-slate-800 text-white',
  },
  'demo-member-jiwoo': {
    name: '김지우',
    role: '프로덕트 리드',
    avatar: 'bg-rose-100 text-rose-700',
  },
  'demo-member-minseo': {
    name: '이민서',
    role: '프로덕트 매니저',
    avatar: 'bg-sky-100 text-sky-700',
  },
  'demo-member-hyun': {
    name: '박현',
    role: '백엔드 엔지니어',
    avatar: 'bg-emerald-100 text-emerald-700',
  },
  'demo-member-sora': {
    name: '정소라',
    role: '프로덕트 디자이너',
    avatar: 'bg-violet-100 text-violet-700',
  },
}

const hash = (s: string): number => {
  const reduced = s.split('').reduce((acc, ch) => (acc * 31 + ch.charCodeAt(0)) | 0, 7)
  return Math.abs(reduced)
}

export const resolveMember = (uuid: string): MemberIdentity => {
  const known = DEMO_MEMBERS[uuid]
  if (known) return known
  const palette = AVATAR_PALETTE[hash(uuid) % AVATAR_PALETTE.length] ?? AVATAR_PALETTE[0]!
  return {
    name: `@${uuid.slice(0, 8)}`,
    role: '멤버',
    avatar: palette,
  }
}

/** Two-character initials for an avatar chip. */
export const memberInitials = (name: string): string => {
  const clean = name.replace(/^@/, '').trim()
  if (!clean) return '?'
  // Korean names: use the last two syllables (family + given start).
  if (/[가-힣]/.test(clean)) return clean.slice(-2)
  const parts = clean.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) return (parts[0]![0]! + parts[1]![0]!).toUpperCase()
  return clean.slice(0, 2).toUpperCase()
}
