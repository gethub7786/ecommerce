import React, { useState } from 'react';
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
  Save
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
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
}

interface PrebuiltIntegration {
  id: string;
  name: string;
  type: 'keystone' | 'cwr' | 'seawide' | 'parts_authority' | 'worldpac' | 'federated';
  description: string;
  icon: string;
  features: string[];
  isPopular?: boolean;
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('suppliers');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierIntegration | null>(null);
  const [showIntegrationDetails, setShowIntegrationDetails] = useState(false);
  const [showAddIntegration, setShowAddIntegration] = useState(false);
  const [selectedPrebuiltIntegration, setSelectedPrebuiltIntegration] = useState<PrebuiltIntegration | null>(null);
  const [showConfigureIntegration, setShowConfigureIntegration] = useState(false);

  const navigationItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 size={20} /> },
    { id: 'suppliers', label: 'Supplier Integrations', icon: <Server size={20} /> },
    { id: 'catalog', label: 'Catalog Management', icon: <Database size={20} /> },
    { id: 'scheduling', label: 'Automation Schedule', icon: <Calendar size={20} /> }
  ];

  const supplierIntegrations: SupplierIntegration[] = [
    {
      id: '1',
      name: 'Keystone Automotive',
      type: 'keystone',
      status: 'active',
      lastSync: '2 hours ago',
      itemCount: 15420,
      locations: 8
    },
    {
      id: '2',
      name: 'CWR Electronics',
      type: 'cwr',
      status: 'syncing',
      lastSync: '15 minutes ago',
      itemCount: 8750,
      locations: 3
    },
    {
      id: '3',
      name: 'Seawide Distribution',
      type: 'seawide',
      status: 'active',
      lastSync: '30 minutes ago',
      itemCount: 12300,
      locations: 5
    }
  ];

  const automationTasks: AutomationTask[] = [
    {
      id: '1',
      name: 'Keystone Catalog Sync',
      type: 'catalog_sync',
      status: 'running',
      progress: 65,
      nextRun: 'In 2 hours',
      supplier: 'Keystone'
    },
    {
      id: '2',
      name: 'CWR Price Update',
      type: 'price_update',
      status: 'scheduled',
      progress: 0,
      nextRun: 'In 45 minutes',
      supplier: 'CWR'
    }
  ];

  const prebuiltIntegrations: PrebuiltIntegration[] = [
    {
      id: 'keystone',
      name: 'Keystone Automotive',
      type: 'keystone',
      description: 'Complete automotive parts integration with real-time inventory and catalog sync',
      icon: '🔧',
      features: ['Real-time inventory', 'Catalog sync', 'Multi-location support', 'FTP backup'],
      isPopular: true
    },
    {
      id: 'cwr',
      name: 'CWR Electronics',
      type: 'cwr',
      description: 'Electronics and electrical components with advanced pricing and availability',
      icon: '⚡',
      features: ['Dynamic pricing', 'Availability tracking', 'Bulk updates', 'API integration']
    },
    {
      id: 'seawide',
      name: 'Seawide Distribution',
      type: 'seawide',
      description: 'Marine and industrial parts distribution with comprehensive location mapping',
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

  const handleSelectPrebuiltIntegration = (integration: PrebuiltIntegration) => {
    setSelectedPrebuiltIntegration(integration);
    setShowConfigureIntegration(true);
    setShowAddIntegration(false);
  };

  const handleSaveIntegration = () => {
    console.log('Saving integration:', selectedPrebuiltIntegration);
    setShowConfigureIntegration(false);
    setSelectedPrebuiltIntegration(null);
    setShowAddIntegration(false);
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Suppliers</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Server className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{automationTasks.length}</p>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <Activity className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderConfigureIntegration = () => {
    if (!selectedPrebuiltIntegration) return null;
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
        <div className="bg-white border rounded-xl shadow-sm p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
            <input type="password" placeholder="Enter API key" className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">API Secret</label>
            <input type="password" placeholder="Enter API secret" className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="flex items-center justify-end space-x-3">
            <button onClick={handleSaveIntegration} className="px-5 py-2 bg-blue-600 text-white rounded-lg flex items-center space-x-2 hover:bg-blue-700">
              <Save size={16} />
              <span>Save Integration</span>
            </button>
          </div>
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
        {prebuiltIntegrations.filter(intg => intg.name.toLowerCase().includes(searchQuery.toLowerCase()) || intg.description.toLowerCase().includes(searchQuery.toLowerCase())).map(intg => (
          <div key={intg.id} className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleSelectPrebuiltIntegration(intg)}>
            {intg.isPopular && <div className="absolute -top-2 -right-2 bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">Popular</div>}
            <div className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-3xl">{intg.icon}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{intg.name}</h3>
                  <p className="text-sm text-gray-500 capitalize">{intg.type} Integration</p>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-4">{intg.description}</p>
              <button className="w-full px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium">Configure Integration</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSupplierIntegrationDetails = () => {
    if (!selectedSupplier) return null;
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
          <div className="flex justify-between"><span className="text-sm text-gray-600">Last Sync:</span><span className="text-sm font-medium text-gray-900">{selectedSupplier.lastSync}</span></div>
          <div className="flex justify-between"><span className="text-sm text-gray-600">Total SKUs:</span><span className="text-sm font-medium text-gray-900">{selectedSupplier.itemCount.toLocaleString()}</span></div>
        </div>
      </div>
    );
  };

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
            <div key={s.id} className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleSupplierClick(s)}>
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
                  <div className="flex justify-between"><span className="text-sm text-gray-600">Total SKUs:</span><span className="text-sm font-medium text-gray-900">{s.itemCount.toLocaleString()}</span></div>
                  <div className="flex justify-between"><span className="text-sm text-gray-600">Locations:</span><span className="text-sm font-medium text-gray-900">{s.locations}</span></div>
                  <div className="flex justify-between"><span className="text-sm text-gray-600">Last Sync:</span><span className="text-sm font-medium text-gray-900">{s.lastSync}</span></div>
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
      case 'suppliers':
        return renderSuppliers();
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
                <button key={item.id} onClick={() => setActiveTab(item.id)} className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${activeTab === item.id ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>{item.icon}<span className="text-sm font-medium">{item.label}</span></button>
              ))}
            </div>
          </nav>
        </div>
        <div className="flex-1">
          <div className="bg-white shadow-sm border-b border-gray-200">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">{navigationItems.find(i => i.id === activeTab)?.label || 'Dashboard'}</h1>
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

