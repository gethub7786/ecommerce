import React, { useState } from 'react'
import { Clock, Loader2, CheckCircle2, XCircle } from 'lucide-react'

interface Props {
  onSchedule: (minutes: number) => Promise<any>
  getSchedule: () => Promise<any>
  label: string
}

export default function ScheduleForm({ onSchedule, getSchedule, label }: Props) {
  const [minutes, setMinutes] = useState('5')
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  // load saved interval on mount
  React.useEffect(() => {
    getSchedule()
      .then((res) => {
        const val = res.data?.interval
        if (val) setMinutes(String(val))
      })
      .catch(() => {})
  }, [])

  const handle = async () => {
    const m = parseInt(minutes, 10) || 0
    setStatus('saving')
    try {
      await onSchedule(m)
      setStatus('success')
      setMessage('Scheduled successfully!')
    } catch {
      setStatus('error')
      setMessage('Failed to schedule')
    }
  }

  const inputCls =
    'w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'

  const feedback = (type: 'success' | 'error') => (
    <div
      className={`flex items-center gap-2 rounded border px-3 py-2 text-sm ${
        type === 'success'
          ? 'border-green-300 bg-green-50 text-green-700'
          : 'border-red-300 bg-red-50 text-red-700'
      }`}
    >
      {type === 'success' ? (
        <CheckCircle2 className="h-4 w-4" />
      ) : (
        <XCircle className="h-4 w-4" />
      )}
      <span>{message}</span>
      <button
        onClick={() => setStatus('idle')}
        className="ml-auto opacity-70 hover:opacity-100"
      >
        ✕
      </button>
    </div>
  )

  return (
    <div className="w-48 space-y-3">
      <div className="flex items-center gap-2">
        <Clock className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          type="number"
          min="1"
          placeholder="Minutes"
          className={inputCls}
          value={minutes}
          onChange={(e) => setMinutes(e.target.value)}
          disabled={status === 'saving'}
        />
      </div>

      <button
        onClick={handle}
        disabled={status === 'saving'}
        className="flex w-full items-center justify-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {status === 'saving' ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        {status === 'saving' ? 'Scheduling…' : label}
      </button>

      {status === 'success' && feedback('success')}
      {status === 'error' && feedback('error')}
    </div>
  )
}
