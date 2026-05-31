import { expect, test } from '@playwright/test'

test('homepage loads and shows Conflow title', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/Conflow/)
})

test('sidebar is visible', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Conflow')).toBeVisible()
})
