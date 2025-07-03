import React, { useState } from 'react'
import { AppBar, Toolbar, Typography, Tabs, Tab, Box, CssBaseline, ThemeProvider, createTheme, Button } from '@mui/material'
import KeystonePage from './keystone/KeystonePage'

const theme = createTheme({ palette: { mode: 'light' } })

export default function App() {
  const [tab, setTab] = useState(0)
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">Automation Tool</Typography>
        </Toolbar>
      </AppBar>
      <Tabs value={tab} onChange={(_,v)=>setTab(v)}>
        <Tab label="Keystone Automotive" />
      </Tabs>
      <Box p={2}>
        {tab === 0 && <KeystonePage />}
      </Box>
    </ThemeProvider>
  )
}
