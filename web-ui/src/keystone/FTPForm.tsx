import React, { useState } from 'react'
import { TextField, Button, Stack } from '@mui/material'
import { saveFtp } from '../api/keystone'

export default function FTPForm() {
  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const [dir, setDir] = useState('/')
  const [file, setFile] = useState('Inventory.csv')
  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      <TextField label="FTP User" value={user} onChange={e=>setUser(e.target.value)} />
      <TextField label="FTP Password" value={password} onChange={e=>setPassword(e.target.value)} />
      <TextField label="Remote Folder" value={dir} onChange={e=>setDir(e.target.value)} />
      <TextField label="Remote File" value={file} onChange={e=>setFile(e.target.value)} />
      <Button variant="contained" onClick={()=>saveFtp(user,password,dir,file)}>Save</Button>
    </Stack>
  )
}
