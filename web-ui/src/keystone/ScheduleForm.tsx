import React from 'react'
import { Button, Stack } from '@mui/material'

interface Props {
  onSchedule: () => Promise<any>
  label: string
}

export default function ScheduleForm({ onSchedule, label }: Props) {
  return (
    <Stack spacing={2}>
      <Button variant="contained" onClick={onSchedule}>{label}</Button>
    </Stack>
  )
}
