import { setActivePinia, createPinia } from 'pinia'
import { useUserProfileStore } from '../userProfile'
import { createResource } from 'frappe-ui'

// Mock frappe-ui's createResource
jest.mock('frappe-ui', () => ({
  createResource: jest.fn(() => ({
    fetch: jest.fn(),
    loading: false,
    error: null,
    data: null
  }))
}))

describe('UserProfile Store', () => {
  beforeEach(() => {
    // creates a fresh pinia and makes it active
    setActivePinia(createPinia())
    // Clear all mocks before each test
    jest.clearAllMocks()
  })

  it('should only make one API call when fetchProfile is called multiple times', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ data: { name: 'Test User' } })

    // Setup the mock resource
    const mockResource = {
      fetch: mockFetch,
      loading: false,
      error: null,
      data: null
    }
    createResource.mockReturnValue(mockResource)

    const store = useUserProfileStore()
    // Replace the store's profile with our mock
    store.profile = mockResource
    store.profileFetched = false

    // Call fetchProfile multiple times
    await store.fetchProfile()
    await store.fetchProlife()
    await store.fetchProlife()

    // Verify that fetch was only called once
    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it('should not make API call if profile is already fetched', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ data: { name: 'Test User' } })

    // Setup the mock resource with data already present
    const mockResource = {
      fetch: mockFetch,
      loading: false,
      error: null,
      data: { name: 'Test User' }
    }
    createResource.mockReturnValue(mockResource)

    const store = useUserProfileStore()
    // Replace the store's profile with our mock
    store.profile = mockResource
    store.profileFetched = true

    // Call fetchProfile
    await store.fetchProlife()

    // Verify that fetch was not called
    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('should not make API call if a fetch is already in progress', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ data: { name: 'Test User' } })

    // Setup the mock resource with loading state
    const mockResource = {
      fetch: mockFetch,
      loading: true,
      error: null,
      data: null
    }
    createResource.mockReturnValue(mockResource)

    const store = useUserProfileStore()
    // Replace the store's profile with our mock
    store.profile = mockResource

    // Call fetchProfile
    await store.fetchProfile()

    // Verify that fetch was not called
    expect(mockFetch).not.toHaveBeenCalled()
  })
})
