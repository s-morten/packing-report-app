'use client'

import Link from 'next/link'
import { useCallback, useEffect, useState } from 'react'

const navItems = [
  { label: 'Odds', href: '/odds' },
  { label: 'My Bets', href: '/bets' },
  { label: 'Profile', href: '/profile' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)

  useEffect(() => {
    setToken(localStorage.getItem('token'))
  }, [])

  const handleAuth = useCallback(async () => {
    const endpoint = isRegister ? '/auth/register' : '/auth/login'
    const res = await fetch(`http://localhost:8000${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) return alert('Auth failed')
    const data = await res.json()
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
      setToken(data.access_token)
    } else {
      alert('Registered — now login')
      setIsRegister(false)
    }
  }, [email, password, isRegister])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-neutral-800">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link href="/odds" className="text-lg font-bold tracking-tight">
            Packing Report
          </Link>
          <ul className="flex items-center gap-6 text-sm">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-neutral-400 transition-colors hover:text-neutral-100">
                  {item.label}
                </Link>
              </li>
            ))}
            {token ? (
              <li>
                <button onClick={handleLogout} className="rounded bg-neutral-800 px-3 py-1.5 text-xs text-neutral-300 hover:bg-neutral-700">
                  Logout
                </button>
              </li>
            ) : (
              <li className="flex items-center gap-2">
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-32 rounded border border-neutral-700 bg-neutral-900 px-2 py-1 text-xs text-neutral-100"
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-32 rounded border border-neutral-700 bg-neutral-900 px-2 py-1 text-xs text-neutral-100"
                />
                <button onClick={handleAuth} className="rounded bg-amber-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-500">
                  {isRegister ? 'Register' : 'Login'}
                </button>
                <button onClick={() => setIsRegister(!isRegister)} className="text-xs text-neutral-500 hover:text-neutral-300">
                  {isRegister ? 'Login instead' : 'Register'}
                </button>
              </li>
            )}
          </ul>
        </nav>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        {children}
      </main>
    </div>
  )
}
