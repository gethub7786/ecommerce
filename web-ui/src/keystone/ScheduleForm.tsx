import React, { useState } from 'react'
import { Button, Stack, TextField } from '@mui/material'

interface Props {
  onSchedule: (minutes: number) => Promise<any>
  label: string
}

export default function ScheduleForm({ onSchedule, label }: Props) {
  const [minutes, setMinutes] = useState('5')
  const handle = () => {
    const m = parseInt(minutes, 10) || 0
    onSchedule(m)
  }
  return (
    <Stack spacing={2} sx={{ width: 200 }}>
      <TextField label="Minutes" value={minutes} onChange={e=>setMinutes(e.target.value)} />
      <Button variant="contained" onClick={handle}>{label}</Button>
    </Stack>
  )
}
