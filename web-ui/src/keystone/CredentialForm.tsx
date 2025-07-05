import React, { useState, useEffect } from 'react'
import { saveCredentials, getCredentials } from '../api/keystone'
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
  const [key, setKey] = useState('')
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  // load saved credentials on mount
  useEffect(() => {
    getCredentials()
      .then((res) => {
        const data = res.data || {}
        setAccount(data.account_number || '')
        setKey(data.security_key || '')
      })
      .catch(() => {})
  }, [])

  const handleSave = async () => {
    if (!account.trim() || !key.trim()) {
      setStatus('error')
      setMessage('Please fill in both Account Number and Security Key')
      return
    }

    setStatus('saving')
    try {
      await saveCredentials(account, key)
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
          onChange={(e) => setAccount(e.target.value)}
          disabled={status === 'saving'}
        />
      </div>

      {/* Security Key */}
      <div className="flex items-center gap-2">
        <KeyIcon className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          type="password"
          placeholder="Security Key"
          className={inputCls}
          value={key}
          onChange={(e) => setKey(e.target.value)}
          disabled={status === 'saving'}
        />
      </div>

      {/* Save */}
      <button
        onClick={handleSave}
        disabled={status === 'saving'}
        className="flex w-full items-center justify-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {status === 'saving' ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Save className="h-4 w-4" />
        )}
        {status === 'saving' ? 'Saving…' : 'Save'}
      </button>

      {status === 'success' && (
        <div className="flex items-center gap-2 rounded border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-700">
          <CheckCircle2 className="h-4 w-4" />
          <span>{message}</span>
          <button
            onClick={clearStatus}
            className="ml-auto text-green-700 hover:opacity-70"
          >
            ✕
          </button>
        </div>
      )}

      {status === 'error' && (
        <div className="flex items-center gap-2 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
          <XCircle className="h-4 w-4" />
          <span>{message}</span>
          <button
            onClick={clearStatus}
            className="ml-auto text-red-700 hover:opacity-70"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  )
}
