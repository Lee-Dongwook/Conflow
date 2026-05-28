import { type ComponentPropsWithoutRef, useState } from 'react'

import { cn } from '../cn'

export type AvatarProps = ComponentPropsWithoutRef<'span'> & {
  readonly label: string
  readonly src?: string | null
  readonly size?: 'sm' | 'md' | 'lg'
}

const sizeClass: Record<NonNullable<AvatarProps['size']>, string> = {
  sm: 'size-8 text-xs',
  md: 'size-10 text-sm',
  lg: 'size-12 text-base',
}

/** Shows two-letter initials from `label` (whitespace-separated words). */
const initialsFromLabel = (label: string): string => {
  const parts = label
    .trim()
    .split(/\s+/)
    .filter((s) => s.length > 0)
  if (parts.length === 0) {
    return '?'
  }
  const head = parts[0]
  if (head === undefined) {
    return '?'
  }
  if (parts.length === 1) {
    return head.slice(0, 2).toUpperCase()
  }
  const tail = parts[parts.length - 1]
  const firstChar = head[0]
  const lastChar = tail?.[0]
  if (firstChar === undefined || lastChar === undefined) {
    return head.slice(0, 2).toUpperCase()
  }
  return `${firstChar}${lastChar}`.toUpperCase()
}

export const Avatar = ({ className, label, src, size = 'md', ...props }: AvatarProps) => {
  const [imgError, setImgError] = useState(false)
  const showImage = !!src && !imgError

  return (
    <span
      role="img"
      aria-label={label}
      className={cn(
        'inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-slate-200 font-medium text-slate-700 ring-2 ring-white',
        sizeClass[size],
        className,
      )}
      {...props}
    >
      {showImage ? (
        <img
          src={src}
          alt={label}
          className="size-full object-cover"
          onError={() => setImgError(true)}
        />
      ) : (
        initialsFromLabel(label)
      )}
    </span>
  )
}
