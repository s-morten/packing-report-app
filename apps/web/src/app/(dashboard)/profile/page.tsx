'use client'

import { useCallback, useEffect, useState } from 'react'

const BASE = 'http://localhost:8000'

function getToken() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem('token') || ''
}

interface Profile {
  id: number
  email: string
}

interface Stats {
  total_bets: number
  won: number
  lost: number
  void: number
  total_stake: number
  total_profit: number
  roi: number
  hit_rate: number
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const token = getToken()

  const fetchProfile = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) setProfile(await res.json())
    else setError('Failed to load profile')
  }, [token])

  const fetchStats = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${BASE}/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      setStats(data)
    }
  }, [token])

  useEffect(() => {
    Promise.all([fetchProfile(), fetchStats()]).finally(() => setLoading(false))
  }, [fetchProfile, fetchStats])

  if (!token) {
    return (
      <section>
        <h1 className="mb-6 text-2xl font-bold">Profile</h1>
        <p className="text-neutral-400">Login or register above to view your profile.</p>
      </section>
    )
  }

  if (loading) {
    return (
      <section>
        <h1 className="mb-6 text-2xl font-bold">Profile</h1>
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 rounded bg-neutral-800" />
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
                <div className="mb-2 h-3 w-16 rounded bg-neutral-800" />
                <div className="h-6 w-20 rounded bg-neutral-800" />
              </div>
            ))}
          </div>
        </div>
      </section>
    )
  }

  return (
    <section>
      <h1 className="mb-6 text-2xl font-bold">Profile</h1>

      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/30 px-4 py-2.5 text-sm text-red-400">
          {error}
        </div>
      )}

      {profile && (
        <div className="mb-8 rounded-lg border border-neutral-800 bg-neutral-900/50 p-5">
          <div className="mb-1 text-xs text-neutral-500">Email</div>
          <div className="text-lg font-medium text-neutral-100">{profile.email}</div>
          <div className="mt-3 text-xs text-neutral-500">User ID</div>
          <div className="text-sm text-neutral-400">#{profile.id}</div>
        </div>
      )}

      {stats && (
        <div>
          <h2 className="mb-3 text-sm font-semibold text-neutral-300">Betting Summary</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
              <p className="text-xs text-neutral-500">Total Bets</p>
              <p className="mt-1 text-2xl font-bold tabular-nums text-neutral-100">{stats.total_bets}</p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
              <p className="text-xs text-neutral-500">Won / Lost</p>
              <p className="mt-1 text-2xl font-bold tabular-nums">
                <span className="text-green-400">{stats.won}</span>
                <span className="text-neutral-500"> / </span>
                <span className="text-red-400">{stats.lost}</span>
              </p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
              <p className="text-xs text-neutral-500">Profit / Loss</p>
              <p className={`mt-1 text-2xl font-bold tabular-nums ${stats.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                €{stats.total_profit.toFixed(2)}
              </p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
              <p className="text-xs text-neutral-500">Hit Rate</p>
              <p className="mt-1 text-2xl font-bold tabular-nums text-amber-400">{stats.hit_rate.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
