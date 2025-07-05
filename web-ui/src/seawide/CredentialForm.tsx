import React, { useState, useEffect } from 'react'
import { saveCredentials, getCredentials } from '../api/seawide'
import {
  Hash,
  Key as KeyIcon,
  Save,
  Loader2,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

export default function CredentialForm() {
  const [account, setAccount] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  // load saved credentials on mount
  useEffect(() => {
    getCredentials()
      .then((res) => {
        const data = res.data || {}
        setAccount(data.account_number || '')
        setApiKey(data.api_key || '')
      })
      .catch(() => {})
  }, [])

  const handleSave = async () => {
    if (!account.trim() || !apiKey.trim()) {
      setStatus('error')
      setMessage('Please fill in both Account Number and API Key')
      return
    }

    setStatus('saving')
    try {
      await saveCredentials(account, apiKey)
      setStatus('success')
      setMessage('Credentials saved successfully!')
    } catch (error: any) {
      setStatus('error')
      setMessage(
        error?.response?.data?.message || 'Failed to save credentials. Please try again.'
      )
    }
  }

  const clearStatus = () => setStatus('idle')

  const inputCls =
    'flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'

  return (
    <div className="w-full max-w-md space-y-4">
      {/* Account Number */}
      <div className="flex items-center gap-2">
        <Hash className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          placeholder="Account Number"
          className={inputCls}
          value={account}
          onChange={e => setAccount(e.target.value)}
          disabled={status === 'saving'}
        />
      </div>
      {/* API Key */}
      <div className="flex items-center gap-2">
        <KeyIcon className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          placeholder="API Key"
          className={inputCls}
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          type="password"
          disabled={status === 'saving'}
        />
      </div>
      {/* Save Button */}
      <button
        className="flex w-full items-center justify-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        onClick={handleSave}
        disabled={status === 'saving'}
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