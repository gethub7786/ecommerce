import React, { useState, useEffect } from 'react';
import KeystonePage from './keystone/KeystonePage';
import CwrPage from './cwr/CwrPage';
import SeawidePage from './seawide/SeawidePage';
import {
  Settings,
  Database,
  Calendar,
  MapPin,
  FileText,
  Activity,
  Server,
  Users,
  BarChart3,
  Bell,
  Search,
  Filter,
  Download,
  Upload,
  Play,
  Pause,
  RefreshCw,
  ArrowLeft,
  Key,
  Wifi,
  HardDrive,
  Clock,
  TestTube,
  CheckCircle,
  AlertCircle,
  PlayCircle,
  Plus,
  X,
  ShoppingCart,
  Globe,
  Cloud,
  Zap,
} from 'lucide-react';
import CatalogPage from './catalog/CatalogPage'
import AmazonInventoryPage from './amazon/AmazonInventoryPage';
import { fetchSupplierStatus, fetchTasks } from './api/keystone';
import dayjs from 'dayjs';
import ProgressBar from './components/ProgressBar';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  active?: boolean;
}

interface SupplierIntegration {
  id: string;
  name: string;
  type: 'keystone' | 'cwr' | 'seawide';
  status: 'active' | 'inactive' | 'error' | 'syncing';
  lastSync: string;
  itemCount: number;
  locations: number;
}

interface AutomationTask {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'completed' | 'failed' | 'scheduled';
  progress: number;
  nextRun: string;
  supplier: string;
  started?: number;
  finished?: number;
}

interface PrebuiltIntegration {
  id: string;
  name: string;
  type:
    | 'keystone'
    | 'cwr'
    | 'seawide'
    | 'parts_authority'
    | 'worldpac'
    | 'federated';
  description: string;
  icon: string;
  features: string[];
  isPopular?: boolean;
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSupplier, setSelectedSupplier] =
    useState<SupplierIntegration | null>(null);
  const [showIntegrationDetails, setShowIntegrationDetails] = useState(false);
  const [showAddIntegration, setShowAddIntegration] = useState(false);
  const [selectedPrebuiltIntegration, setSelectedPrebuiltIntegration] =
    useState<PrebuiltIntegration | null>(null);
  const [showConfigureIntegration, setShowConfigureIntegration] =
    useState(false);

  const navigationItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 size={20} className="text-blue-500" /> },
    { id: 'channel-integration', label: 'Channel Integration', icon: <Globe size={20} className="text-blue-500" /> },
    { id: 'suppliers', label: 'Supplier Integrations', icon: <Server size={20} className="text-blue-500" /> },
    { id: 'catalog', label: 'Catalog Management', icon: <Database size={20} className="text-blue-500" /> },
    { id: 'amazon-inventory', label: 'Amazon Inventory', icon: <ShoppingCart size={20} className="text-blue-500" /> },
    { id: 'sku-mapping', label: 'SKU Mapping', icon: <FileText size={20} className="text-blue-500" /> },
    { id: 'locations', label: 'Multi-Location', icon: <MapPin size={20} className="text-blue-500" /> },
    { id: 'scheduling', label: 'Automation Schedule', icon: <Calendar size={20} className="text-blue-500" /> },
    { id: 'credentials', label: 'FTP Credentials', icon: <Settings size={20} className="text-blue-500" /> },
    { id: 'monitoring', label: 'System Monitoring', icon: <Activity size={20} className="text-blue-500" /> }
  ];

  const [supplierIntegrations, setSupplierIntegrations] =
    useState<SupplierIntegration[]>([])

  const [automationTasks, setAutomationTasks] = useState<AutomationTask[]>([])

  useEffect(() => {
    fetchSupplierStatus().then(res => {
      setSupplierIntegrations(res.data.suppliers || [])
    })
    fetchTasks().then(res => {
      setAutomationTasks(res.data.tasks || [])
      if (res.data.tasks) {
        res.data.tasks.forEach((t: AutomationTask) => console.log(`[DEBUG] Task: ${t.name}, Progress: ${t.progress}, Status: ${t.status}`));
      }
    })
    const id = setInterval(() => {
      fetchSupplierStatus().then(r => setSupplierIntegrations(r.data.suppliers || []))
      fetchTasks().then(r => {
        setAutomationTasks(r.data.tasks || [])
        if (r.data.tasks) {
          r.data.tasks.forEach((t: AutomationTask) => console.log(`[DEBUG] Task: ${t.name}, Progress: ${t.progress}, Status: ${t.status}`));
        }
      })
    }, 1000)
    return () => clearInterval(id)
  }, [])


  const prebuiltIntegrations: PrebuiltIntegration[] = [
    {
      id: 'keystone',
      name: 'Keystone Automotive',
      type: 'keystone',
      description:
        'Complete automotive parts integration with real-time inventory and catalog sync',
      icon: '🔧',
      features: ['Real-time inventory', 'Catalog sync', 'Multi-location support', 'FTP backup'],
      isPopular: true
    },
    {
      id: 'cwr',
      name: 'CWR Electronics',
      type: 'cwr',
      description:
        'Electronics components with advanced pricing and availability',
      icon: '⚡',
      features: ['Dynamic pricing', 'Availability tracking', 'Bulk updates', 'API integration']
    },
    {
      id: 'seawide',
      name: 'Seawide Distribution',
      type: 'seawide',
      description:
        'Marine and industrial parts distribution with comprehensive location mapping',
      icon: '🌊',
      features: ['Location mapping', 'Inventory sync', 'Catalog management', 'Scheduled updates']
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'running':
      case 'completed':
        return 'text-emerald-600 bg-emerald-50 border-emerald-200';
      case 'syncing':
      case 'scheduled':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'error':
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSupplierIcon = (type: string) => {
    switch (type) {
      case 'keystone':
        return '🔧';
      case 'cwr':
        return '⚡';
      case 'seawide':
        return '🌊';
      default:
        return '📦';
    }
  };

  const handleSupplierClick = (supplier: SupplierIntegration) => {
    setSelectedSupplier(supplier);
    setShowIntegrationDetails(true);
  };

  const handleBackToSuppliers = () => {
    setShowIntegrationDetails(false);
    setSelectedSupplier(null);
    setShowAddIntegration(false);
    setShowConfigureIntegration(false);
    setSelectedPrebuiltIntegration(null);
  };

  const handleAddIntegration = () => {
    setShowAddIntegration(true);
  };

  const totalSkus = supplierIntegrations.reduce(
    (sum, s) => sum + s.itemCount,
    0
  );
  const totalLocations = supplierIntegrations.reduce(
    (sum, s) => sum + s.locations,
    0
  );

  // Compute only currently active (running/scheduled) tasks for dashboard count
  const activeTaskCount = automationTasks.filter(t => ['running', 'scheduled'].includes(t.status)).length;

  const handleSelectPrebuiltIntegration = (integration: PrebuiltIntegration) => {
    setSelectedPrebuiltIntegration(integration);
    setShowConfigureIntegration(true);
    setShowAddIntegration(false);
  };


  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Suppliers</p>
              <p className="text-2xl font-bold text-gray-900">{supplierIntegrations.length}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Server className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total SKUs</p>
              <p className="text-2xl font-bold text-gray-900">{totalSkus.toLocaleString()}</p>
            </div>
            <div className="p-3 bg-emerald-50 rounded-lg">
              <Database className="h-6 w-6 text-emerald-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{activeTaskCount}</p>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <Activity className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Locations</p>
              <p className="text-2xl font-bold text-gray-900">{totalLocations}</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <MapPin className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Supplier Integration Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {supplierIntegrations.map(s => (
              <div key={s.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getSupplierIcon(s.type)}</span>
                    <div>
                      <h4 className="font-medium text-gray-900">{s.name}</h4>
                      <p className="text-sm text-gray-500">Last sync: {s.lastSync}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(s.status)}`}>{s.status.charAt(0).toUpperCase() + s.status.slice(1)}</span>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{s.itemCount.toLocaleString()} SKUs</p>
                    <p className="text-xs text-gray-500">{s.locations} locations</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Automation Tasks</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {automationTasks
              .filter(task => task.name.toLowerCase().includes('inventory'))
              .sort((a, b) => {
                // Running tasks first, then most recent completed
                if (a.status === 'running' && b.status !== 'running') return -1;
                if (a.status !== 'running' && b.status === 'running') return 1;
                return (b.finished ?? 0) - (a.finished ?? 0);
              })
              .slice(0, 4) // Show up to 1 running + 3 recent completed
              .map(task => (
                <div key={task.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${task.status === 'running' ? 'bg-blue-50' : task.status === 'completed' ? 'bg-emerald-50' : 'bg-gray-50'}`}>{task.status === 'running' ? <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" /> : task.status === 'completed' ? <Database className="h-4 w-4 text-emerald-600" /> : <Calendar className="h-4 w-4 text-gray-600" />}</div>
                    <div>
                      <h4 className="font-medium text-gray-900">{task.name}</h4>
                      <p className="text-sm text-gray-500">
                        {task.supplier} • Started: {task.started ? dayjs.unix(task.started).format('YYYY-MM-DD HH:mm:ss') : '—'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(task.status)}`}>{task.status.charAt(0).toUpperCase() + task.status.slice(1)}</span>
                    {(task.status === 'running' || task.status === 'completed' || task.status === 'failed') && (
                      <div className="flex items-center gap-2 min-w-[120px]">
                        <ProgressBar percent={task.progress} />
                        <span className="text-xs text-gray-700 w-8 text-right tabular-nums">{task.progress}%</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderCatalogManagement = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Catalog Management</h2>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center space-x-2">
            <Download size={16} />
            <span>Export Catalog</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <RefreshCw size={16} />
            <span>Sync All</span>
          </button>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Catalog Overview</h3>
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input type="text" placeholder="Search SKUs..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <Filter size={16} className="text-gray-600" />
              </button>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Active SKUs</h4>
              <p className="text-2xl font-bold text-emerald-600">34,250</p>
              <p className="text-sm text-gray-500">Last updated 2 hours ago</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Pending Updates</h4>
              <p className="text-2xl font-bold text-orange-600">1,420</p>
              <p className="text-sm text-gray-500">Requires manual review</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Error Items</h4>
              <p className="text-2xl font-bold text-red-600">800</p>
              <p className="text-sm text-gray-500">Failed validation</p>
            </div>
          </div>
          <div className="border border-gray-200 rounded-lg">
            <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
              <div className="grid grid-cols-6 gap-4 text-sm font-medium text-gray-600">
                <div>SKU</div>
                <div>Product Name</div>
                <div>Supplier</div>
                <div>Stock</div>
                <div>Last Updated</div>
                <div>Status</div>
              </div>
            </div>
            <div className="divide-y divide-gray-200">
              {[1, 2, 3, 4, 5].map(item => (
                <div key={item} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="grid grid-cols-6 gap-4 text-sm">
                    <div className="font-mono text-gray-900">SKU-{String(item).padStart(6, '0')}</div>
                    <div className="text-gray-900">Sample Product {item}</div>
                    <div className="text-gray-600">Keystone</div>
                    <div className="text-gray-900">250</div>
                    <div className="text-gray-600">2 hours ago</div>
                    <div>
                      <span className="px-2 py-1 text-xs font-medium rounded-full border bg-emerald-50 text-emerald-600 border-emerald-200">Active</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSupplierIntegrationDetails = () => {
    if (!selectedSupplier) return null;

    // For Keystone, render the full management page inside details
    if (selectedSupplier.type === 'keystone') {
      return (
        <div className="space-y-6">
          <div className="p-4">
            <button
              onClick={handleBackToSuppliers}
              className="inline-flex items-center gap-2 rounded-lg bg-white border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <span className="text-xl">🔧</span>
              <span>Back to Integrations</span>
            </button>
          </div>
          <KeystonePage onBack={handleBackToSuppliers} hideCredentials hideTest />
        </div>
      );
    }

    // default simple details for other suppliers
    return (
      <div className="space-y-6">
        <button onClick={handleBackToSuppliers} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
          <ArrowLeft size={18} />
          <span>Back to suppliers</span>
        </button>
        <div className="flex items-center space-x-3">
          <span className="text-3xl">{getSupplierIcon(selectedSupplier.type)}</span>
          <h2 className="text-2xl font-bold text-gray-900">{selectedSupplier.name}</h2>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Last Sync:</span>
            <span className="text-sm font-medium text-gray-900">{selectedSupplier.lastSync}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Total SKUs:</span>
            <span className="text-sm font-medium text-gray-900">{selectedSupplier.itemCount.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Locations:</span>
            <span className="text-sm font-medium text-gray-900">{selectedSupplier.locations}</span>
          </div>
        </div>
      </div>
    );
  };

  const renderConfigureIntegration = () => {
    if (!selectedPrebuiltIntegration) return null;
    if (selectedPrebuiltIntegration.id === 'keystone') {
      return (
        <div className="space-y-6">
          <KeystonePage setupOnly onBack={handleBackToSuppliers} />
        </div>
      );
    }
    if (selectedPrebuiltIntegration.id === 'cwr') {
      return (
        <div className="space-y-6">
          <button onClick={handleBackToSuppliers} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft size={18} />
            <span>Back to suppliers</span>
          </button>
          <CwrPage onBack={handleBackToSuppliers} />
        </div>
      );
    }
    if (selectedPrebuiltIntegration.id === 'seawide') {
      return (
        <div className="space-y-6">
          <button onClick={handleBackToSuppliers} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft size={18} />
            <span>Back to suppliers</span>
          </button>
          <SeawidePage setupOnly onBack={handleBackToSuppliers} />
        </div>
      );
    }
    return (
      <div className="space-y-6">
        <button onClick={handleBackToSuppliers} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
          <ArrowLeft size={18} />
          <span>Back</span>
        </button>
        <div className="flex items-center space-x-3">
          <span className="text-4xl">{selectedPrebuiltIntegration.icon}</span>
          <h2 className="text-2xl font-bold text-gray-900">Configure: {selectedPrebuiltIntegration.name}</h2>
        </div>
        <div className="bg-white border rounded-xl shadow-sm p-6 space-y-6 text-gray-600">
          <p>Configuration coming soon.</p>
        </div>
      </div>
    );
  };

  const renderAddIntegration = () => (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button onClick={handleBackToSuppliers} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Add New Integration</h2>
          <p className="text-sm text-gray-500">Choose from our prebuilt supplier integrations</p>
        </div>
      </div>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
        <input type="text" placeholder="Search integrations..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {prebuiltIntegrations
          .filter(intg => intg.name.toLowerCase().includes(searchQuery.toLowerCase()) || intg.description.toLowerCase().includes(searchQuery.toLowerCase()))
          .map(intg => (
            <div key={intg.id} onClick={() => handleSelectPrebuiltIntegration(intg)} className="bg-white border rounded-xl shadow-sm hover:shadow-md transition cursor-pointer relative">
              {intg.isPopular && <div className="absolute -top-2 -right-2 bg-orange-500 text-white text-xs px-2 py-1 rounded-full">Popular</div>}
              <div className="p-6 space-y-4">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{intg.icon}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{intg.name}</h3>
                    <p className="text-xs text-gray-500 capitalize">{intg.id} integration</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{intg.description}</p>
                <button onClick={e => { e.stopPropagation(); handleSelectPrebuiltIntegration(intg); }} className="w-full py-2 text-sm font-medium bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100">Configure Integration</button>
              </div>
            </div>
          ))}
      </div>
    </div>
  );

  const renderChannelIntegration = () => (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-8">
      <div className="flex flex-col items-center space-y-4">
        <Globe size={64} className="text-blue-500" />
        <h2 className="text-3xl font-bold text-gray-900">Channel Integration</h2>
        <p className="text-lg text-gray-600 max-w-xl">Connect your business to multiple sales channels with seamless integration, real-time sync, and powerful automation. Easily manage your products, inventory, and orders across all platforms from one beautiful dashboard.</p>
      </div>
      <ul className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl">
        <li className="flex items-center space-x-4 bg-white rounded-xl shadow p-6 border border-gray-100">
          <Zap size={32} className="text-emerald-500" />
          <div className="text-left">
            <h3 className="font-semibold text-gray-900">Real-Time Sync</h3>
            <p className="text-sm text-gray-500">Keep your inventory and orders up-to-date across all channels automatically.</p>
          </div>
        </li>
        <li className="flex items-center space-x-4 bg-white rounded-xl shadow p-6 border border-gray-100">
          <Cloud size={32} className="text-blue-500" />
          <div className="text-left">
            <h3 className="font-semibold text-gray-900">Cloud-Based Management</h3>
            <p className="text-sm text-gray-500">Access and control your integrations from anywhere, anytime.</p>
          </div>
        </li>
      </ul>
    </div>
  );

  const renderSuppliers = () => {
    if (showConfigureIntegration) return renderConfigureIntegration();
    if (showAddIntegration) return renderAddIntegration();
    if (showIntegrationDetails) return renderSupplierIntegrationDetails();
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Supplier Integrations</h2>
          <button onClick={handleAddIntegration} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Plus size={16} />
            <span>Add Integration</span>
          </button>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {supplierIntegrations.map(s => (
            <div key={s.id} onClick={() => handleSupplierClick(s)} className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{getSupplierIcon(s.type)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">{s.name}</h3>
                      <p className="text-sm text-gray-500 capitalize">{s.type} Integration</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(s.status)}`}>{s.status.charAt(0).toUpperCase() + s.status.slice(1)}</span>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total SKUs:</span>
                    <span className="text-sm font-medium text-gray-900">{s.itemCount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Locations:</span>
                    <span className="text-sm font-medium text-gray-900">{s.locations}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Sync:</span>
                    <span className="text-sm font-medium text-gray-900">{s.lastSync}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'channel-integration':
        return renderChannelIntegration();
      case 'suppliers':
        return renderSuppliers();
      case 'catalog':
        return <CatalogPage />;
      case 'amazon-inventory':
        return <AmazonInventoryPage />;
      case 'sku-mapping':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">SKU Mapping Configuration</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <p className="text-gray-600">Configure SKU mapping rules and transformations for supplier integrations.</p>
            </div>
          </div>
        );
      case 'locations':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Multi-Location Management</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <p className="text-gray-600">Manage inventory across multiple warehouse locations and distribution centers.</p>
            </div>
          </div>
        );
      case 'scheduling':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Automation Schedule</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <p className="text-gray-600">Configure automated sync schedules and task management.</p>
            </div>
          </div>
        );
      case 'credentials':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">FTP Credentials</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <p className="text-gray-600">Manage FTP connection credentials for supplier data feeds.</p>
            </div>
          </div>
        );
      case 'monitoring':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">System Monitoring</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <p className="text-gray-600">Monitor system performance, logs, and integration health.</p>
            </div>
          </div>
        );
      default:
        return renderDashboard();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="flex">
        <div className="w-64 bg-white shadow-lg border-r border-gray-200 min-h-screen">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-lg">
                <Server className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">SupplierSync</h1>
                <p className="text-sm text-gray-500">Automation Hub</p>
              </div>
            </div>
          </div>
          <nav className="p-4">
            <div className="space-y-2">
              {navigationItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    activeTab === item.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  {item.icon}
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              ))}
            </div>
          </nav>
        </div>
        <div className="flex-1">
          <div className="bg-white shadow-sm border-b border-gray-200">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">
                    {navigationItems.find(item => item.id === activeTab)?.label || 'Dashboard'}
                  </h1>
                  <p className="text-sm text-gray-500">Manage your supplier integrations and automation</p>
                </div>
                <div className="flex items-center space-x-4">
                  <button className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors">
                    <Bell size={20} />
                    <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span>
                  </button>
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-full flex items-center justify-center">
                      <Users className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Admin User</p>
                      <p className="text-xs text-gray-500">System Administrator</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="p-6">{renderContent()}</div>
        </div>
      </div>
    </div>
  );
};

export default App;

