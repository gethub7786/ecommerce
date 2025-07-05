import React, { useState, useEffect } from 'react'
import { TextField, Button, Stack, Alert, CircularProgress } from '@mui/material'
import { saveCredentials, getCredentials } from '../api/cwr'

export default function CredentialForm() {
  const [feedId, setFeedId] = useState('')
  const [status, setStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  useEffect(() => {
    getCredentials().then(res => setFeedId(res.data.feed_id || '')).catch(()=>{})
  }, [])

  const handleSave = async () => {
    setStatus('saving')
    try {
      await saveCredentials(feedId)
      setStatus('success')
      setMessage('Credentials saved successfully!')
    } catch (error) {
      setStatus('error')
      setMessage('Failed to save credentials.')
    }
  }

  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      <TextField label="Feed ID" value={feedId} onChange={e=>setFeedId(e.target.value)} />
      <Button variant="contained" onClick={handleSave} disabled={status === 'saving'}>
        {status === 'saving' ? <CircularProgress size={24} /> : 'Save'}
      </Button>
      {status === 'success' && <Alert severity="success">{message}</Alert>}
      {status === 'error' && <Alert severity="error">{message}</Alert>}
    </Stack>
  )
} 