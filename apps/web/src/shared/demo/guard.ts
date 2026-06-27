/**
 * Demo write guard.
 *
 * Browsing the demo is free, but write actions (create/edit/delete) must
 * not hit the network. Entity api write wrappers call `blockWrite()` when
 * the workspace is the demo sentinel: it notifies the registered handler
 * (mounted by the demo banner → opens the login modal) and throws so the
 * mutation aborts. One registration point, no per-form plumbing.
 */

export class DemoModeError extends Error {
  constructor() {
    super('demo-mode: 이 작업은 로그인 후 사용할 수 있습니다.')
    this.name = 'DemoModeError'
  }
}

type WriteAttemptHandler = () => void

let handler: WriteAttemptHandler | null = null

export const demoGuard = {
  /** Register (or clear with `null`) the login-prompt handler. */
  setOnWriteAttempt(cb: WriteAttemptHandler | null): void {
    handler = cb
  },
  /** Prompt login and abort the mutation. */
  blockWrite(): never {
    handler?.()
    throw new DemoModeError()
  },
}
