import React, { useState } from 'react'
import { Button } from '@mui/material'
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

import {
  Key,
  HardDrive,
  MapPin,
  Play,
  PlayCircle,
  Wifi,
  Clock,
  FileText,
  Upload,
  CheckCircle,
  ArrowLeft
} from 'lucide-react'

export default function KeystonePage({ onBack }: { onBack?: () => void }) {
  const [tab, setTab] = useState<number>(0)

  const tabs = [
    {
      label: 'Set API Credential',
      icon: <Key size={18} />,
      content: <CredentialForm />
    },
    {
      label: 'Set FTP Credentials',
      icon: <HardDrive size={18} />,
      content: <FTPForm />
    },
    {
      label: 'Configure Location Mapping',
      icon: <MapPin size={18} />,
      content: <LocationMapForm />
    },
    {
      label: 'Run Partial Inventory',
      icon: <Play size={18} />,
      content: <Button variant="contained" onClick={runPartialInventory}>Run</Button>
    },
    {
      label: 'Run Full Inventory',
      icon: <PlayCircle size={18} />,
      content: <Button variant="contained" onClick={runFullInventory}>Run</Button>
    },
    {
      label: 'Run Full Inventory via FTP',
      icon: <Wifi size={18} />,
      content: <Button variant="contained" onClick={runFTPFull}>Run</Button>
    },
    {
      label: 'Schedule Partial Inventory',
      icon: <Clock size={18} />,
      content: <ScheduleForm onSchedule={schedulePartial} label="Schedule" />
    },
    {
      label: 'Schedule Full Inventory',
      icon: <Clock size={18} />,
      content: <ScheduleForm onSchedule={scheduleFull} label="Schedule" />
    },
    {
      label: 'Run Catalog',
      icon: <FileText size={18} />,
      content: <Button variant="contained" onClick={runCatalog}>Run</Button>
    },
    {
      label: 'Schedule Catalog',
      icon: <Clock size={18} />,
      content: <ScheduleForm onSchedule={scheduleCatalog} label="Schedule" />
    },
    {
      label: 'Manage Catalog',
      icon: <CheckCircle size={18} />,
      content: <CatalogManager />
    },
    {
      label: 'Upload Multi-Location Inventory',
      icon: <Upload size={18} />,
      content: <Button variant="contained" onClick={uploadMLI}>Run</Button>
    },
    {
      label: 'Test Connection',
      icon: <CheckCircle size={18} />,
      content: <Button variant="contained" onClick={testConnection}>Test</Button>
    },
    {
      label: 'Back',
      icon: <ArrowLeft size={18} />,
      content: <Button variant="outlined" onClick={onBack}>Back to suppliers</Button>
    }
  ]

  return (
    <div className="flex">
      <div className="w-64 bg-white border-r border-gray-200">
        {tabs.map((t, idx) => (
          <button
            key={idx}
            onClick={() => setTab(idx)}
            className={`w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium transition-colors hover:bg-blue-50 ${
              tab === idx ? 'bg-blue-100 text-blue-700' : 'text-gray-700'
            }`}
          >
            {t.icon}
            <span>{t.label}</span>
          </button>
        ))}
      </div>
      <div className="flex-1 p-6 bg-gray-50 min-h-screen">{tabs[tab].content}</div>
    </div>
  )
}
