import React, { useState } from 'react'
import { TextField, Button, Stack } from '@mui/material'
import { saveCredentials } from '../api/keystone'

export default function CredentialForm() {
  const [account, setAccount] = useState('')
  const [key, setKey] = useState('')
  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      <TextField label="Account Number" value={account} onChange={e=>setAccount(e.target.value)} />
      <TextField label="Security Key" value={key} onChange={e=>setKey(e.target.value)} />
      <Button variant="contained" onClick={()=>saveCredentials(account,key)}>Save</Button>
    </Stack>
  )
}
