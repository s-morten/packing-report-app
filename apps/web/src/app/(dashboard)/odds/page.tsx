'use client'

import { useCallback, useEffect, useState } from 'react'
import { api } from '@/lib/api-client'

interface League {
  id: number
  name: string
  country: string | null
}

interface Team {
  id: number
  name: string
}

interface Event {
  id: number
  league_id: number
  home_team: Team
  away_team: Team
  start_time: string
  status: string
}

interface BookmakerOdds {
  bookmaker_id: number
  bookmaker_name: string
  home: number
  draw: number
  away: number
}

interface OddsData {
  event: Event
  bookmaker_odds: BookmakerOdds[]
}

function formatDateTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function bestOdds(odds: BookmakerOdds[], key: 'home' | 'draw' | 'away') {
  return Math.max(...odds.map((o) => o[key]))
}

export default function OddsPage() {
  const [leagues, setLeagues] = useState<League[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [oddsData, setOddsData] = useState<OddsData | null>(null)
  const [selectedLeague, setSelectedLeague] = useState<string>('')
  const [selectedEvent, setSelectedEvent] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<League[]>('/leagues').then((data) => {
      setLeagues(data)
      if (data.length > 0) {
        setSelectedLeague(String(data[0].id))
      }
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedLeague) return
    api.get<Event[]>(`/events?league_id=${selectedLeague}`).then((data) => {
      setEvents(data)
      setSelectedEvent('')
      setOddsData(null)
      if (data.length > 0) {
        setSelectedEvent(String(data[0].id))
      }
    })
  }, [selectedLeague])

  const fetchOdds = useCallback((eventId: string) => {
    if (!eventId) return
    api.get<OddsData>(`/odds?event_id=${eventId}`).then(setOddsData)
  }, [])

  useEffect(() => {
    fetchOdds(selectedEvent)
  }, [selectedEvent, fetchOdds])

  if (loading) {
    return (
      <section>
        <h1 className="mb-6 text-2xl font-bold">Odds Comparison</h1>
        <p className="text-neutral-400">Loading leagues...</p>
      </section>
    )
  }

  return (
    <section>
      <h1 className="mb-6 text-2xl font-bold">Odds Comparison</h1>

      <div className="mb-6 flex flex-wrap gap-4">
        <select
          value={selectedLeague}
          onChange={(e) => setSelectedLeague(e.target.value)}
          className="rounded-lg border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-neutral-100"
        >
          {leagues.map((l) => (
            <option key={l.id} value={l.id}>
              {l.name} {l.country ? `(${l.country})` : ''}
            </option>
          ))}
        </select>

        {events.length > 0 && (
          <select
            value={selectedEvent}
            onChange={(e) => setSelectedEvent(e.target.value)}
            className="rounded-lg border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-neutral-100"
          >
            {events.map((e) => (
              <option key={e.id} value={e.id}>
                {e.home_team.name} vs {e.away_team.name} — {formatDateTime(e.start_time)}
              </option>
            ))}
          </select>
        )}
      </div>

      {oddsData && (
        <div className="overflow-x-auto rounded-lg border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-neutral-800 bg-neutral-900">
                <th className="px-4 py-3 font-medium text-neutral-400">Bookmaker</th>
                <th className="px-4 py-3 font-medium text-neutral-400 text-right">1</th>
                <th className="px-4 py-3 font-medium text-neutral-400 text-right">X</th>
                <th className="px-4 py-3 font-medium text-neutral-400 text-right">2</th>
              </tr>
            </thead>
            <tbody>
              {oddsData.bookmaker_odds.map((bm) => {
                const bestH = bestOdds(oddsData.bookmaker_odds, 'home')
                const bestD = bestOdds(oddsData.bookmaker_odds, 'draw')
                const bestA = bestOdds(oddsData.bookmaker_odds, 'away')
                return (
                  <tr key={bm.bookmaker_id} className="border-b border-neutral-800 last:border-0">
                    <td className="px-4 py-3 font-medium">{bm.bookmaker_name}</td>
                    <td className={`px-4 py-3 text-right font-mono tabular-nums ${bm.home === bestH ? 'text-amber-400 font-bold' : ''}`}>
                      {bm.home.toFixed(2)}
                    </td>
                    <td className={`px-4 py-3 text-right font-mono tabular-nums ${bm.draw === bestD ? 'text-amber-400 font-bold' : ''}`}>
                      {bm.draw.toFixed(2)}
                    </td>
                    <td className={`px-4 py-3 text-right font-mono tabular-nums ${bm.away === bestA ? 'text-amber-400 font-bold' : ''}`}>
                      {bm.away.toFixed(2)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {events.length === 0 && !loading && (
        <p className="text-neutral-400">No upcoming events for this league.</p>
      )}
    </section>
  )
}
