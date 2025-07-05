import React, { useState } from 'react'
import CredentialForm from './CredentialForm'
import FTPForm from './FTPForm'
import LocationMapForm from './LocationMapForm'
import ScheduleForm from '../keystone/ScheduleForm'
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
  uploadMLI,
  getPartialSchedule,
  getFullSchedule,
  getCatalogSchedule
} from '../api/seawide'
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
  XCircle,
  ArrowLeft
} from 'lucide-react'

function ActionButton({ action, text, success }: { action: () => Promise<any>; text: string; success: string }) {
  const [state, setState] = React.useState<'idle' | 'running' | 'success' | 'error'>('idle')
  const [msg, setMsg] = React.useState('')

  const handle = async () => {
    setState('running')
    setMsg('')
    try {
      await action()
      setState('success')
      setMsg(success)
    } catch (e: any) {
      console.error(e)
      setState('error')
      setMsg('Operation failed')
    }
  }

  const feedbackBanner = (type: 'success' | 'error') => (
    <div
      className={`flex items-center gap-2 rounded border px-3 py-2 text-sm ${
        type === 'success'
          ? 'border-green-300 bg-green-50 text-green-700'
          : 'border-red-300 bg-red-50 text-red-700'
      }`}
    >
      {type === 'success' ? (
        <CheckCircle className="h-4 w-4" />
      ) : (
        <XCircle className="h-4 w-4" />
      )}
      <span>{msg}</span>
      <button
        onClick={() => setState('idle')}
        className="ml-auto opacity-70 hover:opacity-100"
      >
        ✕
      </button>
    </div>
  )

  return (
    <div className="space-y-2">
      <button
        onClick={handle}
        disabled={state === 'running'}
        className="flex w-40 items-center justify-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {state === 'running' && <Play className="h-4 w-4 animate-spin" />}
        {state === 'running' ? 'Running…' : text}
      </button>
      {state === 'success' && feedbackBanner('success')}
      {state === 'error' && feedbackBanner('error')}
    </div>
  )
}

interface SeawidePageProps {
  onBack?: () => void;
  setupOnly?: boolean;
  hideCredentials?: boolean;
  hideTest?: boolean;
}

export default function SeawidePage({ onBack, setupOnly, hideCredentials = false, hideTest = false }: SeawidePageProps) {
  const [tab, setTab] = useState<number>(0)

  // full set of management tabs
  const fullTabs = [
    {
      label: 'Credentials',
      icon: <Key size={18} />,
      content: (
        <div className="space-y-8">
          <CredentialForm />
          <FTPForm />
          <LocationMapForm />
        </div>
      )
    },
    {
      label: 'Inventory',
      icon: <Play size={18} />,
      content: (
        <div className="space-y-4">
          <ActionButton action={runPartialInventory} text="Run Partial" success="Partial inventory completed" />
          <ActionButton action={runFullInventory} text="Run Full" success="Full inventory completed" />
          <ActionButton action={runFTPFull} text="Run via FTP" success="FTP inventory completed" />
          <ActionButton action={uploadMLI} text="Upload MLI" success="MLI file created" />
        </div>
      )
    },
    {
      label: 'Scheduling',
      icon: <Clock size={18} />,
      content: (
        <div className="space-y-4">
          <ScheduleForm onSchedule={schedulePartial} getSchedule={getPartialSchedule} label="Schedule Partial" />
          <ScheduleForm onSchedule={scheduleFull} getSchedule={getFullSchedule} label="Schedule Full" />
          <ScheduleForm onSchedule={scheduleCatalog} getSchedule={getCatalogSchedule} label="Schedule Catalog" />
        </div>
      )
    },
    {
      label: 'Catalog',
      icon: <FileText size={18} />,
      content: (
        <div className="space-y-4">
          <ActionButton action={runCatalog} text="Sync Catalog" success="Catalog sync completed" />
          <CatalogManager />
        </div>
      )
    },
    {
      label: 'Test Connection',
      icon: <Wifi size={18} />,
      content: <ActionButton action={testConnection} text="Test" success="Connection successful" />
    }
  ]

  // limited tabs for initial setup (credentials + test)
  const setupTabs = [
    {
      label: 'Credentials',
      icon: <Key size={18} />,
      content: (
        <div className="space-y-8">
          <CredentialForm />
          <FTPForm />
          <LocationMapForm />
        </div>
      )
    },
    {
      label: 'Test Connection',
      icon: <Wifi size={18} />,
      content: <ActionButton action={testConnection} text="Test" success="Connection successful" />
    }
  ]

  const rawTabs = setupOnly ? setupTabs : fullTabs

  const tabs = rawTabs.filter(
    (t) =>
      !(
        (hideCredentials && t.label === 'Credentials') ||
        (hideTest && t.label === 'Test Connection')
      )
  )

  // Show back button only in setupOnly mode, on the Credentials tab
  const showBackButton = setupOnly && tab === 0 && typeof onBack === 'function';

  return (
    <div className="flex">
      <div className="flex-1">
        {showBackButton && (
          <div className="p-4">
            <button
              onClick={onBack}
              className="inline-flex items-center gap-2 rounded-lg bg-white border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <span className="text-xl">🌊</span>
              <span>Back to Integrations</span>
            </button>
          </div>
        )}
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
      </div>
    </div>
  )
}