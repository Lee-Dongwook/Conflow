/**
 * 404 — shown for any route that doesn't match. Kept intentionally simple:
 * a clear message and two ways back in (home + the browsable demo), so a
 * mistyped or stale shared link still converts instead of dead-ending.
 */

import { Link } from 'react-router-dom'

import { DEMO_WORKSPACE_UUID } from 'app/shared/demo'

export const NotFoundPage = () => (
  <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 text-center">
    <p className="text-6xl font-bold tracking-tight text-teal-600">404</p>
    <h1 className="mt-4 text-xl font-semibold text-slate-900">
      페이지를 찾을 수 없어요
    </h1>
    <p className="mt-2 max-w-sm text-sm text-slate-500">
      주소가 바뀌었거나 삭제된 페이지일 수 있습니다.
    </p>
    <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
      <Link
        to="/"
        className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-teal-700"
      >
        홈으로
      </Link>
      <Link
        to={`/w/${DEMO_WORKSPACE_UUID}`}
        className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
      >
        데모 둘러보기
      </Link>
    </div>
  </div>
)
