import React, { useState, useEffect } from 'react'
import { saveLocationMap, getLocationMap } from '../api/seawide'
import {
  Plus,
  Save,
  Loader2,
  CheckCircle2,
  XCircle,
  Trash2,
} from 'lucide-react'

interface Entry { column: string; source: string }

export default function LocationMapForm() {
  const [entries, setEntries] = useState<Entry[]>([{ column: '', source: '' }])
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  // load existing mapping on mount
  useEffect(() => {
    getLocationMap()
      .then(res => {
        const map: Record<string, string> = res.data || {}
        const list = Object.keys(map).length
          ? Object.entries(map).map(([column, source]) => ({ column, source }))
          : [{ column: '', source: '' }]
        setEntries(list)
      })
      .catch(() => {})
  }, [])

  const handleChange = (i: number, field: 'column' | 'source', value: string) => {
    const next = entries.slice()
    next[i] = { ...next[i], [field]: value }
    setEntries(next)
  }

  const addRow = () => setEntries([...entries, { column: '', source: '' }])

  const removeRow = (idx: number) => {
    if (entries.length === 1) return
    const next = entries.filter((_, i) => i !== idx)
    setEntries(next)
  }

  const handleSave = async () => {
    const map: Record<string, string> = {}
    entries.forEach(e => {
      if (e.column && e.source) map[e.column] = e.source
    })

    setStatus('saving')
    try {
      await saveLocationMap(map)
      setStatus('success')
      setMessage('Location mapping saved successfully!')
    } catch (err: any) {
      setStatus('error')
      setMessage(
        err?.response?.data?.message || 'Failed to save location mapping.'
      )
    }
  }

  const clearStatus = () => setStatus('idle')

  const inputCls =
    'flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'

  return (
    <div className="w-full max-w-md space-y-4">
      {entries.map((e, idx) => (
        <div key={idx} className="flex items-center gap-2">
          <input
            placeholder="Column Name"
            className={inputCls}
            value={e.column}
            onChange={(ev) => handleChange(idx, 'column', ev.target.value)}
            disabled={status === 'saving'}
          />
          <input
            placeholder="Supply Source ID"
            className={inputCls}
            value={e.source}
            onChange={(ev) => handleChange(idx, 'source', ev.target.value)}
            disabled={status === 'saving'}
          />
          <button
            className="p-2 rounded hover:bg-red-100"
            onClick={() => removeRow(idx)}
            disabled={entries.length === 1 || status === 'saving'}
            type="button"
          >
            <Trash2 className="h-5 w-5 text-red-400" />
          </button>
        </div>
      ))}
      <button
        onClick={addRow}
        disabled={status === 'saving'}
        className="flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
        type="button"
      >
        <Plus className="h-4 w-4" /> Add row
      </button>
      <button
        className="flex w-full items-center justify-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        onClick={handleSave}
        disabled={status === 'saving'}
        type="button"
      >
        {status === 'saving' ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Save className="h-4 w-4" />
        )}
        {status === 'saving' ? 'Saving…' : 'Save'}
      </button>
      {/* Status Message */}
      {status === 'success' && (
        <div className="flex items-center gap-2 rounded bg-green-100 px-3 py-2 text-green-800">
          <CheckCircle2 className="h-5 w-5" />
          <span>{message}</span>
          <button className="ml-auto" onClick={clearStatus}>
            <XCircle className="h-5 w-5 text-green-400 hover:text-green-600" />
          </button>
        </div>
      )}
      {status === 'error' && (
        <div className="flex items-center gap-2 rounded bg-red-100 px-3 py-2 text-red-800">
          <XCircle className="h-5 w-5" />
          <span>{message}</span>
          <button className="ml-auto" onClick={clearStatus}>
            <XCircle className="h-5 w-5 text-red-400 hover:text-red-600" />
          </button>
        </div>
      )}
    </div>
  )
}