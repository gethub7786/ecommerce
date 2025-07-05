import React, { useState } from 'react'
import { TextField, Button, Stack } from '@mui/material'
import { saveFtp } from '../api/cwr'

export default function FTPForm() {
  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const [port, setPort] = useState('22')
  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      <TextField label="FTP User" value={user} onChange={e=>setUser(e.target.value)} />
      <TextField label="FTP Password" value={password} onChange={e=>setPassword(e.target.value)} />
      <TextField label="Port" value={port} onChange={e=>setPort(e.target.value)} />
      <Button variant="contained" onClick={()=>saveFtp(user,password,port)}>Save</Button>
    </Stack>
  )
} 