import { useState, useEffect } from 'react'

interface HealthResponse {
  status: string
  app: string
  version: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchHealth() {
      try {
        const response = await fetch('/api/health')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setHealth(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }
    fetchHealth()
  }, [])

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>Error: {error}</div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Signal Lens</h1>
        <p style={styles.subtitle}>AI Agent Workflow Orchestration</p>
      </header>
      <main style={styles.main}>
        <section style={styles.card}>
          <h2 style={styles.sectionTitle}>System Health</h2>
          <dl style={styles.dl}>
            <div style={styles.row}>
              <dt style={styles.dt}>Status</dt>
              <dd style={styles.dd}>{health?.status}</dd>
            </div>
            <div style={styles.row}>
              <dt style={styles.dt}>Application</dt>
              <dd style={styles.dd}>{health?.app}</dd>
            </div>
            <div style={styles.row}>
              <dt style={styles.dt}>Version</dt>
              <dd style={styles.dd}>{health?.version}</dd>
            </div>
          </dl>
        </section>
      </main>
      <footer style={styles.footer}>
        <p>Ryan Vo &lt;ryandtvo@gmail.com&gt; | AI &amp; Machine Learning</p>
      </footer>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    backgroundColor: '#f8f9fa',
    color: '#212529',
  },
  header: {
    padding: '2rem 1rem',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderBottom: '1px solid #dee2e6',
  },
  title: {
    margin: 0,
    fontSize: '2.5rem',
    fontWeight: 700,
    color: '#1a1a2e',
  },
  subtitle: {
    margin: '0.5rem 0 0',
    fontSize: '1.125rem',
    color: '#6c757d',
  },
  main: {
    flex: 1,
    padding: '2rem 1rem',
    maxWidth: '800px',
    width: '100%',
    margin: '0 auto',
    boxSizing: 'border-box',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '1.5rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    border: '1px solid #e9ecef',
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: '1rem',
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#343a40',
  },
  dl: {
    margin: 0,
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '0.5rem 0',
    borderBottom: '1px solid #f1f3f4',
  },
  dt: {
    fontWeight: 500,
    color: '#495057',
  },
  dd: {
    margin: 0,
    fontFamily: 'monospace',
    color: '#212529',
  },
  footer: {
    padding: '1.5rem',
    textAlign: 'center',
    color: '#6c757d',
    fontSize: '0.875rem',
    borderTop: '1px solid #dee2e6',
    backgroundColor: '#fff',
  },
  loading: {
    fontSize: '1.25rem',
    color: '#6c757d',
  },
  error: {
    color: '#dc3545',
    fontSize: '1.125rem',
  },
}

export default App
