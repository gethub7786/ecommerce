import React, { useState } from 'react'
import { TextField, Button, Stack, IconButton } from '@mui/material'
import { saveLocationMap } from '../api/cwr'
import AddIcon from '@mui/icons-material/Add'

interface Entry { column: string; source: string }

export default function LocationMapForm() {
  const [entries, setEntries] = useState<Entry[]>([{ column: '', source: '' }])

  const handleChange = (i: number, field: 'column' | 'source', value: string) => {
    const next = entries.slice()
    next[i] = { ...next[i], [field]: value }
    setEntries(next)
  }

  const addRow = () => setEntries([...entries, { column: '', source: '' }])

  const handleSave = () => {
    const map: Record<string, string> = {}
    entries.forEach(e => {
      if (e.column && e.source) map[e.column] = e.source
    })
    saveLocationMap(map)
  }

  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      {entries.map((e, idx) => (
        <Stack key={idx} direction="row" spacing={1}>
          <TextField label="Column Name" value={e.column} onChange={ev=>handleChange(idx,'column',ev.target.value)} />
          <TextField label="Supply Source ID" value={e.source} onChange={ev=>handleChange(idx,'source',ev.target.value)} />
        </Stack>
      ))}
      <IconButton onClick={addRow}><AddIcon /></IconButton>
      <Button variant="contained" onClick={handleSave}>Save</Button>
    </Stack>
  )
} 