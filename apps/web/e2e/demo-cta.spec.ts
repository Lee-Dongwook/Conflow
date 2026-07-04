import { expect, test } from '@playwright/test'

// Clicks the landing-page CTA by its id, then asserts it navigates into the
// demo workspace. When the button's id is renamed in the component, the
// `#enter-demo-btn` selector below breaks — the healer should re-point the
// selector while leaving the `toHaveURL` assertion untouched.
test('guest enters the demo workspace from the landing CTA', async ({ page }) => {
  await page.goto('/')
  await page.click('#demo-cta-btn')
  await expect(page).toHaveURL(/\/w\//)
})
