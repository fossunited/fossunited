// Mock window.frappe
global.window = {
  frappe: {
    csrf_token: 'test-token'
  }
}

// Mock console methods to keep test output clean
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn()
}
