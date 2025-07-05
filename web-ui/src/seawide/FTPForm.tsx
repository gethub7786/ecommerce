import React, { useState, useEffect } from 'react'
import { saveFtp, getFtp } from '../api/seawide'
import {
  User,
  Lock,
  Folder,
  FileText,
  Save,
  Loader2,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

export default function FTPForm() {
  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const [dir, setDir] = useState('/')
  const [file, setFile] = useState('Inventory.csv')
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  // load saved creds on mount
  useEffect(() => {
    getFtp()
      .then((res: { data?: any }) => {
        const d = res.data || {}
        setUser(d.user || '')
        setPassword(d.password || '')
        setDir(d.remote_dir || '/')
        setFile(d.remote_file || 'Inventory.csv')
      })
      .catch(() => {})
  }, [])

  const handleSave = async () => {
    if (!user.trim() || !password.trim()) {
      setStatus('error')
      setMessage('Please enter both FTP user and password')
      return
    }

    setStatus('saving')
    try {
      await saveFtp(user, password, dir, file)
      setStatus('success')
      setMessage('FTP credentials saved successfully!')
    } catch {
      setStatus('error')
      setMessage('Failed to save credentials')
    }
  }

  const resetStatus = () => setStatus('idle')

  const inputCls =
    'flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'

  return (
    <div className="w-full max-w-md space-y-4">
      {/* User */}
      <div className="flex items-center gap-2">
        <User className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          placeholder="FTP User"
          className={inputCls}
          value={user}
          onChange={e => setUser(e.target.value)}
          disabled={status === 'saving'}
        />
      </div>
      {/* Password */}
      <div className="flex items-center gap-2">
        <Lock className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          placeholder="FTP Password"
          className={inputCls}
          value={password}
          onChange={e => setPassword(e.target.value)}
          type="password"
          disabled={status === 'saving'}
        />
      </div>
      {/* Remote Folder */}
      <div className="flex items-center gap-2">
        <Folder className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          placeholder="Remote Folder"
          className={inputCls}
          value={dir}
          onChange={e => setDir(e.target.value)}
          disabled={status === 'saving'}
        />
      </div>
      {/* Remote File */}
      <div className="flex items-center gap-2">
        <FileText className="h-5 w-5 shrink-0 text-gray-500" />
        <input
          placeholder="Remote File"
          className={inputCls}
          value={file}
          onChange={e => setFile(e.target.value)}
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
          <button className="ml-auto" onClick={resetStatus}>
            <XCircle className="h-5 w-5 text-green-400 hover:text-green-600" />
          </button>
        </div>
      )}
      {status === 'error' && (
        <div className="flex items-center gap-2 rounded bg-red-100 px-3 py-2 text-red-800">
          <XCircle className="h-5 w-5" />
          <span>{message}</span>
          <button className="ml-auto" onClick={resetStatus}>
            <XCircle className="h-5 w-5 text-red-400 hover:text-red-600" />
          </button>
        </div>
      )}
    </div>
  )
}