import React, { useState } from 'react'
import { TextField, Button, Stack } from '@mui/material'
import { saveLocationMap } from '../api/keystone'

export default function LocationMapForm() {
  const [json, setJson] = useState('{}')
  const handleSave = () => {
    try {
      const obj = JSON.parse(json)
      saveLocationMap(obj)
    } catch (e) {
      alert('Invalid JSON')
    }
  }
  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      <TextField label="Location Mapping JSON" multiline minRows={4} value={json} onChange={e=>setJson(e.target.value)} />
      <Button variant="contained" onClick={handleSave}>Save</Button>
    </Stack>
  )
}
