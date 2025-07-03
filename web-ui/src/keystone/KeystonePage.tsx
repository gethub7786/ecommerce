import React, { useState } from 'react'
import { Box, Tabs, Tab } from '@mui/material'
import CredentialForm from './CredentialForm'
import FTPForm from './FTPForm'
import LocationMapForm from './LocationMapForm'
import ScheduleForm from './ScheduleForm'
import CatalogManager from './CatalogManager'
import {
  runPartialInventory,
  runFullInventory,
  runFTPFull,
  runCatalog,
  testConnection,
  schedulePartial,
  scheduleFull,
  scheduleCatalog,
  uploadMLI
} from '../api/keystone'

export default function KeystonePage() {
  const [action, setAction] = useState(0)
  return (
    <Box sx={{ display: 'flex' }}>
      <Tabs orientation="vertical" value={action} onChange={(_,v)=>setAction(v)}>
        <Tab label="Set API Credential" />
        <Tab label="Set FTP Credentials" />
        <Tab label="Configure Location Mapping" />
        <Tab label="Run Partial Inventory" />
        <Tab label="Run Full Inventory" />
        <Tab label="Run Full Inventory via FTP" />
        <Tab label="Schedule Partial Inventory" />
        <Tab label="Schedule Full Inventory" />
        <Tab label="RUN CATALOG" />
        <Tab label="Schedule Catalog" />
        <Tab label="Manage Catalog" />
        <Tab label="Upload Multi-Location Inventory" />
        <Tab label="Test Connection" />
        <Tab label="Back" />
      </Tabs>
      <Box sx={{ flexGrow:1, p:2 }}>
        {action===0 && <CredentialForm />}
        {action===1 && <FTPForm />}
        {action===2 && <LocationMapForm />}
        {action===3 && <button onClick={runPartialInventory}>Run</button>}
        {action===4 && <button onClick={runFullInventory}>Run</button>}
        {action===5 && <button onClick={runFTPFull}>Run</button>}
        {action===6 && <ScheduleForm onSchedule={schedulePartial} label="Schedule" />}
        {action===7 && <ScheduleForm onSchedule={scheduleFull} label="Schedule" />}
        {action===8 && <button onClick={runCatalog}>Run</button>}
        {action===9 && <ScheduleForm onSchedule={scheduleCatalog} label="Schedule" />}
        {action===10 && <CatalogManager />}
        {action===11 && <button onClick={uploadMLI}>Run</button>}
        {action===12 && <button onClick={testConnection}>Test</button>}
        {action===13 && <div>Select another supplier from the top tabs.</div>}
      </Box>
    </Box>
  )
}
