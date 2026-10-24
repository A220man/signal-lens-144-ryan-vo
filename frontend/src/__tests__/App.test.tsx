import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../App'

// Mock fetch globally
global.fetch = vi.fn()

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('shows loading state initially', () => {
    ;(fetch as vi.Mock).mockImplementation(() => new Promise(() => {})) // never resolves
    render(<App />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays health data when fetch succeeds', async () => {
    const mockHealth = {
      status: 'healthy',
      app: 'signal-lens-144-ryan-vo',
      version: '1.0.0',
    }
    ;(fetch as vi.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockHealth),
    })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('System Health')).toBeInTheDocument()
    })

    expect(screen.getByText('healthy')).toBeInTheDocument()
    expect(screen.getByText('signal-lens-144-ryan-vo')).toBeInTheDocument()
    expect(screen.getByText('1.0.0')).toBeInTheDocument()
  })

  it('displays error when fetch fails', async () => {
    ;(fetch as vi.Mock).mockRejectedValue(new Error('Network error'))

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument()
    })
  })
})
