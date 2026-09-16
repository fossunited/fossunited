#!/usr/bin/env node

import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { chromium } from 'playwright-core'

const defaults = {
  baseUrl: 'http://fossunited.localhost:8000',
  width: 1440,
  height: 1050,
  timeout: 30_000,
  settle: 1_000,
}

const help = `Capture a local FOSS United dashboard page with Playwright.

Usage:
  yarn screenshot-dashboard --url <path-or-url> --output <file> [options]

Options:
  --url <value>              Route or absolute URL to capture (required)
  --output <file>            Standard screenshot path (required)
  --base-url <url>           Local site URL (${defaults.baseUrl})
  --email <email>            Login email (or SCREENSHOT_EMAIL)
  --password <password>      Login password (or SCREENSHOT_PASSWORD)
  --wait-for-text <text>     Wait until visible text appears
  --wait-for <selector>      Wait until a CSS selector is visible
  --target <selector>        Capture one element instead of the viewport
  --click-button <name>      Click a button after the standard screenshot
  --expanded-output <file>   Capture again after --click-button
  --expanded-target <css>    Element to capture after clicking
  --mock-file <file>         JSON response routes for deterministic captures
  --width <pixels>           Viewport width (${defaults.width})
  --height <pixels>          Viewport height (${defaults.height})
  --timeout <milliseconds>   Navigation and locator timeout (${defaults.timeout})
  --settle <milliseconds>   Pause before each capture (${defaults.settle})
  --full-page                Capture the full page
  --headed                   Show the browser while capturing
  --browser <file>           Chromium executable (or PLAYWRIGHT_CHROMIUM_EXECUTABLE)
  --help                     Show this help

Mock file format:
  {"routes":[{"url":"**/api/method/example","status":200,"json":{"message":{}}}]}
`

function parseArgs(argv) {
  const options = { ...defaults, fullPage: false, headed: false }
  const names = {
    '--url': 'url',
    '--output': 'output',
    '--base-url': 'baseUrl',
    '--email': 'email',
    '--password': 'password',
    '--wait-for-text': 'waitForText',
    '--wait-for': 'waitFor',
    '--target': 'target',
    '--click-button': 'clickButton',
    '--expanded-output': 'expandedOutput',
    '--expanded-target': 'expandedTarget',
    '--mock-file': 'mockFile',
    '--width': 'width',
    '--height': 'height',
    '--timeout': 'timeout',
    '--settle': 'settle',
    '--browser': 'browser',
  }

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index]
    if (argument === '--help') options.help = true
    else if (argument === '--full-page') options.fullPage = true
    else if (argument === '--headed') options.headed = true
    else if (names[argument]) {
      const value = argv[index + 1]
      if (!value || value.startsWith('--'))
        throw new Error(`${argument} requires a value`)
      options[names[argument]] = value
      index += 1
    } else throw new Error(`Unknown option: ${argument}`)
  }

  for (const key of ['width', 'height', 'timeout', 'settle']) {
    options[key] = Number(options[key])
    const minimum = key === 'settle' ? 0 : 1
    if (!Number.isInteger(options[key]) || options[key] < minimum) {
      throw new Error(
        `--${key.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)} must be at least ${minimum}`,
      )
    }
  }
  return options
}

function findBrowser(explicitPath) {
  const candidates = [
    explicitPath,
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome',
    `${process.env.HOME}/.local/bin/chromium`,
  ].filter(Boolean)
  return candidates.find(existsSync)
}

async function installMocks(page, mockFile) {
  if (!mockFile) return
  const config = JSON.parse(readFileSync(resolve(mockFile), 'utf8'))
  if (!Array.isArray(config.routes))
    throw new Error('Mock file must contain a routes array')

  for (const routeConfig of config.routes) {
    if (!routeConfig.url)
      throw new Error('Every mock route needs a url pattern')
    await page.route(routeConfig.url, (route) =>
      route.fulfill({
        status: routeConfig.status ?? 200,
        contentType: routeConfig.contentType ?? 'application/json',
        body: routeConfig.body ?? JSON.stringify(routeConfig.json ?? {}),
      }),
    )
  }
}

async function logIn(page, baseUrl, email, password) {
  if (!email && !password) return
  if (!email || !password)
    throw new Error('Both email and password are required for login')

  await page.goto(new URL('/login', baseUrl).href, {
    waitUntil: 'domcontentloaded',
  })
  const result = await page.evaluate(
    async ({ username, userPassword }) => {
      const response = await fetch('/api/method/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ usr: username, pwd: userPassword }),
      })
      return {
        ok: response.ok,
        status: response.status,
        body: await response.text(),
      }
    },
    { username: email, userPassword: password },
  )
  if (!result.ok)
    throw new Error(`Login failed (${result.status}): ${result.body}`)
}

async function capture(page, output, target, fullPage) {
  const filename = resolve(output)
  mkdirSync(dirname(filename), { recursive: true })
  if (target) await page.locator(target).screenshot({ path: filename })
  else await page.screenshot({ path: filename, fullPage })
  console.log(filename)
}

async function main() {
  const options = parseArgs(process.argv.slice(2))
  if (options.help) {
    console.log(help)
    return
  }
  if (!options.url || !options.output)
    throw new Error('--url and --output are required')
  if (Boolean(options.clickButton) !== Boolean(options.expandedOutput)) {
    throw new Error(
      '--click-button and --expanded-output must be used together',
    )
  }

  const browserPath = findBrowser(options.browser)
  const browser = await chromium.launch({
    ...(browserPath ? { executablePath: browserPath } : {}),
    headless: !options.headed,
  })

  try {
    const page = await browser.newPage({
      viewport: { width: options.width, height: options.height },
      deviceScaleFactor: 1,
    })
    page.setDefaultTimeout(options.timeout)
    await installMocks(page, options.mockFile)
    await logIn(
      page,
      options.baseUrl,
      options.email ?? process.env.SCREENSHOT_EMAIL,
      options.password ?? process.env.SCREENSHOT_PASSWORD,
    )

    const url = new URL(options.url, options.baseUrl).href
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: options.timeout,
    })
    if (options.waitForText)
      await page.getByText(options.waitForText).first().waitFor()
    if (options.waitFor) await page.locator(options.waitFor).first().waitFor()
    await page.waitForTimeout(options.settle)
    await capture(page, options.output, options.target, options.fullPage)

    if (options.clickButton) {
      await page
        .getByRole('button', { name: options.clickButton, exact: true })
        .click()
      await page.waitForTimeout(options.settle)
      await capture(
        page,
        options.expandedOutput,
        options.expandedTarget,
        options.fullPage,
      )
    }
  } finally {
    await browser.close()
  }
}

main().catch((error) => {
  console.error(error.message)
  process.exitCode = 1
})
