'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface Bet {
  id: number
  home_team: string
  away_team: string
  stake: number
  odds: number
  selection: string
  status: string
  placed_at: string
  settled_at: string | null
  game_id: number | null
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

interface GameResult {
  id: number
  home_team: string
  away_team: string
  date: string
  goals_home: number
  goals_away: number
}

interface TeamStatsItem {
  team: string
  total_bets: number
  won: number
  lost: number
  money_won: number
  money_lost: number
}

interface SelectionStatsItem {
  selection: string
  total_bets: number
  won: number
  lost: number
  money_won: number
  money_lost: number
}

interface OddsBucketItem {
  bucket: string
  total_bets: number
  won: number
  lost: number
  money_won: number
  money_lost: number
}

const BASE = 'http://localhost:8000'
const PAGE_SIZE = 10

function getToken() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem('token') || ''
}

function formatDT(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

const statusColors: Record<string, string> = {
  open: 'bg-blue-500/20 text-blue-400',
  won: 'bg-green-500/20 text-green-400',
  lost: 'bg-red-500/20 text-red-400',
  void: 'bg-neutral-500/20 text-neutral-400',
}

function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-neutral-800 ${className}`} />
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
  const [loadingBets, setLoadingBets] = useState(true)
  const [loadingStats, setLoadingStats] = useState(true)
  const [betsError, setBetsError] = useState('')
  const [statsError, setStatsError] = useState('')
  const [formError, setFormError] = useState('')
  const [teamAnalysis, setTeamAnalysis] = useState<{ by_team: TeamStatsItem[]; by_selection: SelectionStatsItem[]; by_odds: OddsBucketItem[] } | null>(null)
  const [loadingTeamAnalysis, setLoadingTeamAnalysis] = useState(true)

  const [gameQ, setGameQ] = useState('')
  const [gameSuggestions, setGameSuggestions] = useState<GameResult[]>([])
  const [selectedGame, setSelectedGame] = useState<GameResult | null>(null)
  const [showGameDropdown, setShowGameDropdown] = useState(false)
  const [searchEmpty, setSearchEmpty] = useState(false)
  const [showManual, setShowManual] = useState(false)
  const gameTimer = useRef<ReturnType<typeof setTimeout>>()
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [selection, setSelection] = useState('home')
  const [stake, setStake] = useState('')
  const [odds, setOdds] = useState('')
  const [placedAt, setPlacedAt] = useState('')
  const [placing, setPlacing] = useState(false)
  const [placedMsg, setPlacedMsg] = useState<{ home: string; away: string; time: string } | null>(null)
  const [offset, setOffset] = useState(0)
  const token = getToken()

  useEffect(() => {
    clearTimeout(gameTimer.current)
    if (selectedGame || gameQ.length < 1) { setGameSuggestions([]); setSearchEmpty(false); return }
    gameTimer.current = setTimeout(async () => {
      const res = await fetch(`${BASE}/games/search?q=${encodeURIComponent(gameQ)}`)
      if (res.ok) {
        const data: GameResult[] = await res.json()
        setGameSuggestions(data)
        setSearchEmpty(data.length === 0)
      }
    }, 200)
    return () => clearTimeout(gameTimer.current)
  }, [gameQ, selectedGame])

  const pickGame = (g: GameResult) => {
    setSelectedGame(g)
    setHomeTeam(g.home_team)
    setAwayTeam(g.away_team)
    setPlacedAt(g.date.slice(0, 10))
    setGameQ(`${g.home_team} vs ${g.away_team}`)
    setGameSuggestions([])
    setSearchEmpty(false)
    setShowManual(false)
  }

  const clearGame = () => {
    setSelectedGame(null)
    setHomeTeam('')
    setAwayTeam('')
    setPlacedAt('')
    setGameQ('')
    setShowManual(true)
  }

  const fetchBets = useCallback(async (pageOffset: number) => {
    if (!token) return
    setLoadingBets(true)
    setBetsError('')
    const res = await fetch(`${BASE}/bets?offset=${pageOffset}&limit=${PAGE_SIZE}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    setLoadingBets(false)
    if (res.ok) setBets(await res.json())
    else setBetsError('Failed to load bets')
  }, [token])

  const fetchStats = useCallback(async () => {
    if (!token) return
    setLoadingStats(true)
    setStatsError('')
    const res = await fetch(`${BASE}/stats`, { headers: { Authorization: `Bearer ${token}` } })
    setLoadingStats(false)
    if (res.ok) setStats(await res.json())
    else setStatsError('Failed to load stats')
  }, [token])

  const fetchTeamAnalysis = useCallback(async () => {
    if (!token) return
    setLoadingTeamAnalysis(true)
    const res = await fetch(`${BASE}/stats/teams`, { headers: { Authorization: `Bearer ${token}` } })
    setLoadingTeamAnalysis(false)
    if (res.ok) setTeamAnalysis(await res.json())
  }, [token])

  useEffect(() => { fetchBets(0); fetchStats(); fetchTeamAnalysis() }, [fetchBets, fetchStats, fetchTeamAnalysis])

  const handlePlaceBet = async () => {
    if (!token || !stake || !odds) return
    if (!homeTeam || !awayTeam) return
    setPlacing(true)
    setFormError('')
    const res = await fetch(`${BASE}/bets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        home_team: homeTeam,
        away_team: awayTeam,
        stake: Number(stake),
        odds: Number(odds),
        selection,
        placed_at: placedAt ? new Date(placedAt).toISOString() : null,
        game_id: selectedGame?.id ?? null,
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
      setSelection('home')
      setGameQ('')
      setSelectedGame(null)
      setShowManual(false)
      setPlacedMsg({ home: created.home_team, away: created.away_team, time: formatDT(created.placed_at) })
      setTimeout(() => setPlacedMsg(null), 4000)
      setOffset(0)
      fetchBets(0)
      fetchStats()
      fetchTeamAnalysis()
    } else {
      const err = await res.json()
      setFormError(err.error?.message || 'Failed to place bet')
    }
  }

  const handleSettle = async (betId: number, status: string) => {
    const res = await fetch(`${BASE}/bets/${betId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status }),
    })
    if (res.ok) { fetchBets(offset); fetchStats(); fetchTeamAnalysis() }
  }

  const totalPages = bets ? Math.ceil(bets.total / PAGE_SIZE) : 0
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1

  const deducedResult = (() => {
    if (!selectedGame) return null
    const { goals_home, goals_away } = selectedGame
    if (goals_home == null || goals_away == null) return 'open'
    if (goals_home > goals_away) return selection === 'home' ? 'won' : 'lost'
    if (goals_home < goals_away) return selection === 'away' ? 'won' : 'lost'
    return selection === 'draw' ? 'won' : 'lost'
  })()

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
          <div className="relative w-80">
            <label className="mb-1 block text-xs text-neutral-500">Search Game {selectedGame ? '(linked)' : ''}</label>
            <input
              type="text"
              value={gameQ}
              onChange={(e) => { setGameQ(e.target.value); setSelectedGame(null); setSearchEmpty(false); setShowManual(false) }}
              onFocus={() => setShowGameDropdown(true)}
              onBlur={() => setTimeout(() => setShowGameDropdown(false), 200)}
              placeholder="e.g. Bayern vs Dortmund"
              className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100"
            />
            {showGameDropdown && gameSuggestions.length > 0 && (
              <div className="absolute left-0 right-0 top-full z-10 mt-0.5 max-h-60 overflow-y-auto rounded border border-neutral-700 bg-neutral-900 shadow-lg">
                {gameSuggestions.map((g) => (
                  <button
                    key={g.id}
                    type="button"
                    onMouseDown={() => pickGame(g)}
                    className="block w-full px-3 py-2 text-left text-sm text-neutral-200 hover:bg-neutral-800"
                  >
                    <span className="font-medium">{g.home_team}</span>
                    <span className="text-neutral-500"> vs </span>
                    <span className="font-medium">{g.away_team}</span>
                    <span className="ml-2 text-xs text-neutral-500">
                      {g.goals_home}-{g.goals_away} &middot; {formatDate(g.date)}
                    </span>
                  </button>
                ))}
              </div>
            )}
            {selectedGame && (
              <p className="mt-1 text-xs text-emerald-400">
                {selectedGame.home_team} {selectedGame.goals_home}-{selectedGame.goals_away} {selectedGame.away_team} &middot; {formatDate(selectedGame.date)}
                <button onClick={clearGame} className="ml-2 text-neutral-500 hover:text-neutral-300">clear</button>
              </p>
            )}
            {searchEmpty && !selectedGame && (
              <p className="mt-1 text-xs text-neutral-500">
                No games found.{' '}
                <button onClick={() => setShowManual(true)} className="text-amber-400 hover:text-amber-300">
                  Add game manually
                </button>
              </p>
            )}
          </div>

          {showManual && !selectedGame && (
            <>
              <div className="w-44">
                <label className="mb-1 block text-xs text-neutral-500">Home Team (manual)</label>
                <input type="text" value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)}
                  placeholder="e.g. Bayern Munich"
                  className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100" />
              </div>
              <div className="w-44">
                <label className="mb-1 block text-xs text-neutral-500">Away Team (manual)</label>
                <input type="text" value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)}
                  placeholder="e.g. Dortmund"
                  className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100" />
              </div>
              <div className="w-44">
                <label className="mb-1 block text-xs text-neutral-500">Bet Taken</label>
                <input type="date" value={placedAt} onChange={(e) => setPlacedAt(e.target.value)}
                  className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100 [color-scheme:dark]" />
              </div>
            </>
          )}

          <div className="w-28">
            <label className="mb-1 block text-xs text-neutral-500">Selection</label>
            <select value={selection} onChange={(e) => setSelection(e.target.value)}
              className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100">
              <option value="home">Home</option>
              <option value="draw">Draw</option>
              <option value="away">Away</option>
            </select>
          </div>

          <div className="w-24">
            <label className="mb-1 block text-xs text-neutral-500">Odd</label>
            <input type="number" step="0.01" placeholder="1.80" value={odds} onChange={(e) => setOdds(e.target.value)}
              className="w-full rounded border border-neutral-700 bg-neutral-800 px-2.5 py-1.5 text-sm text-neutral-100" />
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

        {deducedResult && (
          <p className="mt-2 text-xs">
            Result:{' '}
            <span className={deducedResult === 'won' ? 'text-green-400' : deducedResult === 'lost' ? 'text-red-400' : 'text-blue-400'}>
              {deducedResult.toUpperCase()}
            </span>
            {deducedResult !== 'open' && ' (auto-deduced from game)'}
          </p>
        )}

        {formError && (
          <p className="mt-2 text-xs text-red-400">{formError}</p>
        )}
      </div>

      <h2 className="mb-3 text-sm font-semibold text-neutral-300">Bet History</h2>

      {betsError && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/30 px-4 py-2.5 text-sm text-red-400">
          {betsError}
        </div>
      )}

      {loadingBets ? (
        <div className="overflow-hidden rounded-lg border border-neutral-800">
          <div className="border-b border-neutral-800 bg-neutral-900 px-3 py-2.5">
            <Skeleton className="h-4 w-96" />
          </div>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-4 border-b border-neutral-800 px-3 py-3">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-14" />
              <Skeleton className="h-4 w-24" />
            </div>
          ))}
        </div>
      ) : bets && (
        <>
          <p className="mb-3 text-sm text-neutral-500">{bets.total} bet{bets.total !== 1 ? 's' : ''}</p>
          <div className="overflow-x-auto rounded-lg border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-neutral-800 bg-neutral-900">
                  <th className="px-3 py-2.5 font-medium text-neutral-400">Match</th>
                  <th className="px-3 py-2.5 font-medium text-neutral-400 text-right">Pick</th>
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
                {bets.items.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-3 py-8 text-center text-sm text-neutral-500">
                      No bets yet. Track your first bet above.
                    </td>
                  </tr>
                ) : bets.items.map(bet => (
                  <tr key={bet.id} className="border-b border-neutral-800 last:border-0">
                    <td className="px-3 py-2.5 font-medium">{bet.home_team} vs {bet.away_team}</td>
                    <td className="px-3 py-2.5 text-right text-xs text-neutral-400 uppercase">{bet.selection}</td>
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

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between text-sm">
              <p className="text-neutral-500">
                Page {currentPage} of {totalPages}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => { const next = Math.max(0, offset - PAGE_SIZE); setOffset(next); fetchBets(next) }}
                  disabled={offset === 0}
                  className="rounded border border-neutral-700 bg-neutral-800 px-3 py-1.5 text-xs text-neutral-300 hover:bg-neutral-700 disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  onClick={() => { const next = offset + PAGE_SIZE; setOffset(next); fetchBets(next) }}
                  disabled={offset + PAGE_SIZE >= bets.total}
                  className="rounded border border-neutral-700 bg-neutral-800 px-3 py-1.5 text-xs text-neutral-300 hover:bg-neutral-700 disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {statsError && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/30 px-4 py-2.5 text-sm text-red-400">
          {statsError}
        </div>
      )}

      {loadingStats ? (
        <div className="mb-8">
          <Skeleton className="mb-3 h-4 w-24" />
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
                <Skeleton className="mb-2 h-3 w-16" />
                <Skeleton className="h-6 w-20" />
              </div>
            ))}
          </div>
          <Skeleton className="mt-6 h-72 w-full rounded-lg" />
        </div>
      ) : stats && (
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

      {loadingTeamAnalysis ? (
        <div className="mb-8">
          <Skeleton className="mb-3 h-4 w-32" />
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-4">
                <Skeleton className="mb-2 h-3 w-16" />
                <Skeleton className="h-6 w-20" />
              </div>
            ))}
          </div>
        </div>
      ) : teamAnalysis && (
        <div className="mb-8">
          <h2 className="mb-3 text-sm font-semibold text-neutral-300">Analysis</h2>
          <div className="overflow-x-auto rounded-lg border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-neutral-800 bg-neutral-900">
                  <th className="px-3 py-2 font-medium text-neutral-400">Category</th>
                  <th className="px-3 py-2 font-medium text-neutral-400 text-right">Bets</th>
                  <th className="px-3 py-2 font-medium text-neutral-400 text-right">Won</th>
                  <th className="px-3 py-2 font-medium text-neutral-400 text-right">Lost</th>
                  <th className="px-3 py-2 font-medium text-neutral-400 text-right">Money Won</th>
                  <th className="px-3 py-2 font-medium text-neutral-400 text-right">Money Lost</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-neutral-800 bg-neutral-900/30">
                  <td className="px-3 py-2 text-xs font-semibold text-neutral-500" colSpan={6}>By Team</td>
                </tr>
                {teamAnalysis.by_team.map(t => (
                  <tr key={t.team} className="border-b border-neutral-800 last:border-0">
                    <td className="px-3 py-2 font-medium">{t.team}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums">{t.total_bets}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-green-400">{t.won}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-red-400">{t.lost}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-green-400">
                      +€{t.money_won.toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-red-400">
                      -€{t.money_lost.toFixed(2)}
                    </td>
                  </tr>
                ))}
                <tr className="border-b border-neutral-800 bg-neutral-900/30">
                  <td className="px-3 py-2 text-xs font-semibold text-neutral-500" colSpan={6}>By Selection</td>
                </tr>
                {teamAnalysis.by_selection.map(s => (
                  <tr key={s.selection} className="border-b border-neutral-800 last:border-0">
                    <td className="px-3 py-2 font-medium capitalize">{s.selection}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums">{s.total_bets}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-green-400">{s.won}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-red-400">{s.lost}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-green-400">
                      +€{s.money_won.toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-red-400">
                      -€{s.money_lost.toFixed(2)}
                    </td>
                  </tr>
                ))}
                <tr className="border-b border-neutral-800 bg-neutral-900/30">
                  <td className="px-3 py-2 text-xs font-semibold text-neutral-500" colSpan={6}>By Odds Range</td>
                </tr>
                {teamAnalysis.by_odds.map(o => (
                  <tr key={o.bucket} className="border-b border-neutral-800 last:border-0">
                    <td className="px-3 py-2 font-medium">{o.bucket}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums">{o.total_bets}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-green-400">{o.won}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-red-400">{o.lost}</td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-green-400">
                      +€{o.money_won.toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono tabular-nums text-red-400">
                      -€{o.money_lost.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  )
}
