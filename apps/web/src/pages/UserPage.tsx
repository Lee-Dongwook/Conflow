import { type ChangeEvent, type FormEvent, useCallback, useEffect, useRef, useState } from 'react'

import {
  Avatar,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Separator,
} from '@conflow/ui'

import { useSession } from 'app/entities/session'
import type { UserWithTeamsRead } from 'app/entities/user'
import { userApi } from 'app/entities/user'

export const UserPage = () => {
  const session = useSession()
  const [user, setUser] = useState<UserWithTeamsRead | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const fetchUser = useCallback(async () => {
    try {
      const me = await userApi.me()
      setUser(me)
      setName(me.name)
    } catch {
      // user not found — may not be fully registered yet
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (session.status === 'authenticated') {
      fetchUser()
    }
  }, [session.status, fetchUser])

  const handleSaveName = async (e: FormEvent) => {
    e.preventDefault()
    if (!user || !name.trim() || name === user.name) {
      setEditing(false)
      return
    }
    setSaving(true)
    try {
      const updated = await userApi.updateMe({ name: name.trim() })
      setUser((prev) => (prev ? { ...prev, ...updated } : prev))
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleAvatarClick = () => {
    fileRef.current?.click()
  }

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const updated = await userApi.uploadAvatar(file)
      setUser((prev) => (prev ? { ...prev, ...updated } : prev))
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  if (session.status !== 'authenticated' || loading) {
    return (
      <div className="flex items-center justify-center py-20 text-sm text-slate-400">
        로딩 중...
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center py-20 text-sm text-slate-400">
        사용자 정보를 불러올 수 없습니다.
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Card className="overflow-hidden">
        <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:gap-8">
          <button
            type="button"
            className="group relative cursor-pointer"
            onClick={handleAvatarClick}
            disabled={uploading}
          >
            <Avatar label={user.name} src={user.profileImageUrl} size="lg" />
            <span className="absolute inset-0 flex items-center justify-center rounded-full bg-black/40 text-[10px] font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
              {uploading ? '...' : '변경'}
            </span>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
          </button>

          <div className="min-w-0 flex-1 space-y-2">
            {editing ? (
              <form onSubmit={handleSaveName} className="flex items-center gap-2">
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="max-w-[200px]"
                  autoFocus
                />
                <Button type="submit" className="px-2 py-1 text-xs" disabled={saving}>
                  {saving ? '저장 중...' : '저장'}
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  className="px-2 py-1 text-xs"
                  onClick={() => {
                    setName(user.name)
                    setEditing(false)
                  }}
                >
                  취소
                </Button>
              </form>
            ) : (
              <div>
                <h2 className="text-xl font-semibold text-slate-900">{user.name}</h2>
                <p className="text-sm text-slate-500">{user.email}</p>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{user.role}</Badge>
            </div>
          </div>

          {!editing && (
            <div className="flex shrink-0 flex-col gap-2 sm:items-end">
              <Button type="button" variant="secondary" onClick={() => setEditing(true)}>
                프로필 수정
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>기본 정보</CardTitle>
          <CardDescription>계정에 연결된 정보입니다.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <Row label="이메일" value={user.email} />
          <Separator />
          <Row label="가입일" value={new Date(user.createdAt).toLocaleDateString('ko-KR')} />
          <Separator />
          <Row label="마지막 수정" value={new Date(user.updatedAt).toLocaleDateString('ko-KR')} />
        </CardContent>
      </Card>

      {user.teamMemberships && user.teamMemberships.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>소속 팀</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {user.teamMemberships.map((tm) => (
              <div
                key={tm.uuid}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-100 bg-slate-50/80 px-3 py-2"
              >
                <span className="font-medium text-slate-900">{tm.teamUuid}</span>
                <Badge variant="outline">{tm.role}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

const Row = ({ label, value }: { readonly label: string; readonly value: string }) => (
  <div className="flex flex-wrap items-center justify-between gap-2">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-900">{value}</span>
  </div>
)
