import React, { useState } from 'react'
import { Box, Tabs, Tab } from '@mui/material'
import CredentialForm from './CredentialForm'
import FTPForm from './FTPForm'
import { runPartialInventory, runFullInventory, runFTPFull, runCatalog, testConnection } from '../api/keystone'

export default function KeystonePage() {
  const [action, setAction] = useState(0)
  return (
    <Box sx={{ display: 'flex' }}>
      <Tabs orientation="vertical" value={action} onChange={(_,v)=>setAction(v)}>
        <Tab label="Set API Credential" />
        <Tab label="Set FTP Credentials" />
        <Tab label="Run Partial Inventory" />
        <Tab label="Run Full Inventory" />
        <Tab label="Run Full Inventory via FTP" />
        <Tab label="RUN CATALOG" />
        <Tab label="Test Connection" />
      </Tabs>
      <Box sx={{ flexGrow:1, p:2 }}>
        {action===0 && <CredentialForm />}
        {action===1 && <FTPForm />}
        {action===2 && <button onClick={runPartialInventory}>Run</button>}
        {action===3 && <button onClick={runFullInventory}>Run</button>}
        {action===4 && <button onClick={runFTPFull}>Run</button>}
        {action===5 && <button onClick={runCatalog}>Run</button>}
        {action===6 && <button onClick={testConnection}>Test</button>}
      </Box>
    </Box>
  )
}
