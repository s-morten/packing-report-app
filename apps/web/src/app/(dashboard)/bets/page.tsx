'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface Bet {
  id: number
  home_team: string
  away_team: string
  stake: number
  odds: number
  status: string
  placed_at: string
  settled_at: string | null
}

interface PaginatedBets {
  items: Bet[]
  total: number
  offset: number
  limit: number
}

interface TimeSeriesPoint {
  date: string
  cumulative_profit: number
  cumulative_stake: number
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
  max_drawdown: number
  time_series: TimeSeriesPoint[]
}

const BASE = 'http://localhost:8000'

function getToken() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem('token') || ''
}

function formatDT(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

const statusColors: Record<string, string> = {
  open: 'bg-blue-500/20 text-blue-400',
  won: 'bg-green-500/20 text-green-400',
  lost: 'bg-red-500/20 text-red-400',
  void: 'bg-neutral-500/20 text-neutral-400',
}

function TeamInput({
  value, onChange, placeholder,
}: {
  value: string
  onChange: (v: string) => void
  placeholder: string
}) {
  const [suggestions, setSuggestions] = useState<{ id: number; name: string }[]>([])
  const [focused, setFocused] = useState(false)
  const timer = useRef<ReturnType<typeof setTimeout>>()

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 1) { setSuggestions([]); return }
    const res = await fetch(`${BASE}/teams?q=${encodeURIComponent(q)}`)
    if (res.ok) setSuggestions(await res.json())
  }, [])

  useEffect(() => {
    clearTimeout(timer.current)
    timer.current = setTimeout(() => fetchSuggestions(value), 150)
    return () => clearTimeout(timer.current)
  }, [value, fetchSuggestions])

  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder={placeholder}
        className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100"
      />
      {focused && suggestions.length > 0 && (
        <div className="absolute left-0 right-0 top-full z-10 mt-0.5 rounded border border-neutral-700 bg-neutral-900 shadow-lg">
          {suggestions.map((s) => (
            <button
              key={s.id}
              type="button"
              onMouseDown={() => onChange(s.name)}
              className="block w-full px-3 py-1.5 text-left text-sm text-neutral-200 hover:bg-neutral-800"
            >
              {s.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function MetricBox({ label, value, color = 'text-neutral-100' }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold tabular-nums ${color}`}>{value}</p>
    </div>
  )
}

export default function BetsPage() {
  const [bets, setBets] = useState<PaginatedBets | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [stake, setStake] = useState('')
  const [odds, setOdds] = useState('')
  const [placedAt, setPlacedAt] = useState('')
  const [placing, setPlacing] = useState(false)
  const [placedMsg, setPlacedMsg] = useState<{ home: string; away: string; time: string } | null>(null)
  const token = getToken()

  const fetchBets = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${BASE}/bets`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) setBets(await res.json())
  }, [token])

  const fetchStats = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${BASE}/stats`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) setStats(await res.json())
  }, [token])

  useEffect(() => { fetchBets(); fetchStats() }, [fetchBets, fetchStats])

  const handlePlaceBet = async () => {
    if (!token || !homeTeam || !awayTeam || !stake || !odds) return
    setPlacing(true)
    const res = await fetch(`${BASE}/bets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        home_team: homeTeam,
        away_team: awayTeam,
        stake: Number(stake),
        odds: Number(odds),
        placed_at: placedAt ? new Date(placedAt).toISOString() : null,
      }),
    })
    setPlacing(false)
    if (res.ok) {
      const created = await res.json()
      setHomeTeam('')
      setAwayTeam('')
      setStake('')
      setOdds('')
      setPlacedAt('')
      setPlacedMsg({ home: created.home_team, away: created.away_team, time: formatDT(created.placed_at) })
      setTimeout(() => setPlacedMsg(null), 4000)
      fetchBets()
      fetchStats()
    } else {
      const err = await res.json()
      alert(err.error?.message || 'Failed to place bet')
    }
  }

  const handleSettle = async (betId: number, status: string) => {
    const res = await fetch(`${BASE}/bets/${betId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status }),
    })
    if (res.ok) { fetchBets(); fetchStats() }
  }

  if (!token) {
    return (
      <section>
        <h1 className="mb-6 text-2xl font-bold">My Bets</h1>
        <p className="text-neutral-400">Login or register above to track your bets.</p>
      </section>
    )
  }

  const profitColor = stats ? (stats.total_profit >= 0 ? 'text-green-400' : 'text-red-400') : 'text-neutral-100'

  return (
    <section>
      <h1 className="mb-6 text-2xl font-bold">My Bets</h1>

      {placedMsg && (
        <div className="mb-4 rounded-lg border border-emerald-700 bg-emerald-900/40 px-4 py-2.5 text-sm text-emerald-300">
          Bet placed — {placedMsg.home} vs {placedMsg.away} on {placedMsg.time}
        </div>
      )}

      <div className="mb-8 rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
        <h2 className="mb-3 text-sm font-semibold text-neutral-300">Track a Bet</h2>
        <div className="flex flex-wrap items-end gap-3">
          <div className="w-44">
            <label className="mb-1 block text-xs text-neutral-500">Home Team</label>
            <TeamInput value={homeTeam} onChange={setHomeTeam} placeholder="e.g. Bayern Munich" />
          </div>
          <div className="w-44">
            <label className="mb-1 block text-xs text-neutral-500">Away Team</label>
            <TeamInput value={awayTeam} onChange={setAwayTeam} placeholder="e.g. Dortmund" />
          </div>
          <div className="w-24">
            <label className="mb-1 block text-xs text-neutral-500">Odd</label>
            <input type="number" step="0.01" placeholder="1.80" value={odds} onChange={(e) => setOdds(e.target.value)}
              className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100" />
          </div>
          <div className="w-44">
            <label className="mb-1 block text-xs text-neutral-500">Bet Taken</label>
            <input type="date" value={placedAt} onChange={(e) => setPlacedAt(e.target.value)}
              className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100 [color-scheme:dark]" />
          </div>
          <div className="w-24">
            <label className="mb-1 block text-xs text-neutral-500">Value (€)</label>
            <input type="number" placeholder="50" value={stake} onChange={(e) => setStake(e.target.value)}
              className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100" />
          </div>
          <button onClick={handlePlaceBet} disabled={placing}
            className="rounded bg-amber-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-amber-500 disabled:opacity-50">
            {placing ? 'Adding...' : 'Track Bet'}
          </button>
        </div>
      </div>

      {bets && (
        <>
          <h2 className="mb-3 text-sm font-semibold text-neutral-300">Bet History</h2>
          <p className="mb-3 text-sm text-neutral-500">{bets.total} bet{bets.total !== 1 ? 's' : ''}</p>
          <div className="overflow-x-auto rounded-lg border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-neutral-800 bg-neutral-900">
                  <th className="px-3 py-2.5 font-medium text-neutral-400">Match</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400 text-right">Stake</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400 text-right">Odds</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400 text-right">To Win</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400 text-right">P/L</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400 text-right">Status</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400">Bet Taken</th>
                  {bets.items.some(b => b.status === 'open') && <th className="px-3 py-2.5" />}
                </tr>
              </thead>
              <tbody>
                {bets.items.map(bet => (
                  <tr key={bet.id} className="border-b border-neutral-800 last:border-0">
                    <td className="px-3 py-2.5 font-medium">{bet.home_team} vs {bet.away_team}</td>
                    <td className="px-3 py-2.5 text-right font-mono tabular-nums">€{bet.stake.toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-right font-mono tabular-nums">{bet.odds.toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-right font-mono tabular-nums text-neutral-100">
                      €{(bet.stake * bet.odds).toFixed(2)}
                    </td>
                    <td className="px-3 py-2.5 text-right font-mono tabular-nums">
                      {bet.status === 'won'
                        ? <span className="text-green-400">+€{(bet.stake * bet.odds - bet.stake).toFixed(2)}</span>
                        : bet.status === 'lost'
                          ? <span className="text-red-400">-€{bet.stake.toFixed(2)}</span>
                          : <span className="text-neutral-500">—</span>
                      }
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[bet.status] || ''}`}>
                        {bet.status}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-xs text-neutral-500">{formatDT(bet.placed_at)}</td>
                    {bet.status === 'open' && (
                      <td className="px-3 py-2.5">
                        <div className="flex gap-1">
                          <button onClick={() => handleSettle(bet.id, 'won')} className="rounded bg-green-600/20 px-2 py-0.5 text-xs text-green-400 hover:bg-green-600/30">Won</button>
                          <button onClick={() => handleSettle(bet.id, 'lost')} className="rounded bg-red-600/20 px-2 py-0.5 text-xs text-red-400 hover:bg-red-600/30">Lost</button>
                          <button onClick={() => handleSettle(bet.id, 'void')} className="rounded bg-neutral-600/20 px-2 py-0.5 text-xs text-neutral-400 hover:bg-neutral-600/30">Void</button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {stats && (
        <div className="mb-8">
          <h2 className="mb-3 text-sm font-semibold text-neutral-300">Performance</h2>
          <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            <MetricBox label="Total Bets" value={stats.total_bets} />
            <MetricBox label="Won" value={stats.won} color="text-green-400" />
            <MetricBox label="Lost" value={stats.lost} color="text-red-400" />
            <MetricBox label="Void" value={stats.void} />
            <MetricBox label="Total Stake" value={`€${stats.total_stake.toFixed(2)}`} />
            <MetricBox label="Profit / Loss" value={`€${stats.total_profit.toFixed(2)}`} color={profitColor} />
            <MetricBox label="ROI" value={`${stats.roi.toFixed(1)}%`} color={stats.roi >= 0 ? 'text-green-400' : 'text-red-400'} />
            <MetricBox label="Hit Rate" value={`${stats.hit_rate.toFixed(1)}%`} color="text-amber-400" />
            <MetricBox label="Max Drawdown" value={`€${stats.max_drawdown.toFixed(2)}`} color="text-red-400" />
          </div>

          {stats.time_series.length > 1 && (
            <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
              <h2 className="mb-4 text-sm font-semibold text-neutral-300">Cumulative Profit</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.time_series}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#888' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#888' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: '#ccc' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="cumulative_profit"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
