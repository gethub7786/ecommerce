import React, { useState, useEffect } from 'react';
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
  RefreshCw
} from 'lucide-react';
import { listCatalog } from './api/keystone';

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

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [skuCount, setSkuCount] = useState(0);
  const [supplierIntegrations, setSupplierIntegrations] = useState<SupplierIntegration[]>([]);

  useEffect(() => {
    listCatalog()
      .then(res => {
        const rows = res.data.rows || [];
        setSkuCount(rows.length);
      })
      .catch(() => setSkuCount(0));
  }, []);

  const navigationItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 size={20} /> },
    { id: 'suppliers', label: 'Supplier Integrations', icon: <Server size={20} /> },
    { id: 'catalog', label: 'Catalog Management', icon: <Database size={20} /> },
    { id: 'sku-mapping', label: 'SKU Mapping', icon: <FileText size={20} /> },
    { id: 'locations', label: 'Multi-Location', icon: <MapPin size={20} /> },
    { id: 'scheduling', label: 'Automation Schedule', icon: <Calendar size={20} /> },
    { id: 'credentials', label: 'FTP Credentials', icon: <Settings size={20} /> },
    { id: 'monitoring', label: 'System Monitoring', icon: <Activity size={20} /> },
  ];

  useEffect(() => {
    fetch('/suppliers/status')
      .then(res => res.json())
      .then(data => setSupplierIntegrations(data.suppliers || []))
      .catch(() => setSupplierIntegrations([]));
  }, []);

  const [automationTasks, setAutomationTasks] = useState<AutomationTask[]>([]);

  useEffect(() => {
    const load = () => {
      fetch('/tasks')
        .then(res => res.json())
        .then(data => setAutomationTasks(data.tasks || []))
        .catch(() => setAutomationTasks([]));
    };
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, []);

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
      case 'inactive':
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

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'suppliers':
        return renderSuppliers();
      case 'catalog':
        return renderCatalogManagement();
      case 'sku-mapping':
        return <div className="p-6">SKU Mapping configuration coming soon...</div>;
      case 'locations':
        return <div className="p-6">Multi-location management coming soon...</div>;
      case 'scheduling':
        return <div className="p-6">Scheduling options coming soon...</div>;
      case 'credentials':
        return <div className="p-6">FTP credentials management coming soon...</div>;
      case 'monitoring':
        return <div className="p-6">System monitoring coming soon...</div>;
      default:
        return null;
    }
  };

  const totalSuppliers = supplierIntegrations.length;
  const activeTaskCount = automationTasks.filter(
    (t) => t.status === 'running' || t.status === 'scheduled'
  ).length;
  const locationCount = supplierIntegrations.reduce(
    (sum, s) => sum + s.locations,
    0
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Suppliers</p>
              <p className="text-2xl font-bold text-gray-900">{totalSuppliers}</p>
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
              <p className="text-2xl font-bold text-gray-900">{skuCount.toLocaleString()}</p>
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
              <p className="text-2xl font-bold text-gray-900">{locationCount}</p>
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
            {supplierIntegrations.map(supplier => (
              <div key={supplier.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getSupplierIcon(supplier.type)}</span>
                    <div>
                      <h4 className="font-medium text-gray-900">{supplier.name}</h4>
                      <p className="text-sm text-gray-500">Last sync: {supplier.lastSync}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(supplier.status)}`}>
                    {supplier.status.charAt(0).toUpperCase() + supplier.status.slice(1)}
                  </span>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{supplier.itemCount.toLocaleString()} SKUs</p>
                    <p className="text-xs text-gray-500">{supplier.locations} locations</p>
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
            {automationTasks.length === 0 && (
              <p className="text-sm text-gray-600">No tasks</p>
            )}
            {automationTasks.map(task => (
              <div key={task.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`p-2 rounded-lg ${task.status === 'running' ? 'bg-blue-50' : task.status === 'completed' ? 'bg-emerald-50' : 'bg-gray-50'}`}> 
                    {task.status === 'running' ? <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" /> :
                     task.status === 'completed' ? <Database className="h-4 w-4 text-emerald-600" /> :
                     <Calendar className="h-4 w-4 text-gray-600" />}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{task.name}</h4>
                    <p className="text-sm text-gray-500">{task.supplier} • Next run: {task.nextRun}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  {task.status === 'running' && (
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full transition-all duration-300" style={{ width: `${task.progress}%` }}></div>
                      </div>
                      <span className="text-sm text-gray-600">{task.progress}%</span>
                    </div>
                  )}
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(task.status)}`}>
                    {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderSuppliers = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Supplier Integrations</h2>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
          <Upload size={16} />
          <span>Add Integration</span>
        </button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {supplierIntegrations.map(supplier => (
          <div key={supplier.id} className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{getSupplierIcon(supplier.type)}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{supplier.name}</h3>
                    <p className="text-sm text-gray-500 capitalize">{supplier.type} Integration</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(supplier.status)}`}>{supplier.status.charAt(0).toUpperCase() + supplier.status.slice(1)}</span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total SKUs:</span>
                  <span className="text-sm font-medium text-gray-900">{supplier.itemCount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Locations:</span>
                  <span className="text-sm font-medium text-gray-900">{supplier.locations}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Last Sync:</span>
                  <span className="text-sm font-medium text-gray-900">{supplier.lastSync}</span>
                </div>
              </div>
              <div className="mt-6 flex space-x-2">
                <button className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium">Configure</button>
                <button className="flex-1 px-3 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors text-sm font-medium">Sync Now</button>
              </div>
            </div>
          </div>
        ))}
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
              {[1,2,3,4,5].map(item => (
                <div key={item} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="grid grid-cols-6 gap-4 text-sm">
                    <div className="font-mono text-gray-900">SKU-{String(item).padStart(6,'0')}</div>
                    <div className="text-gray-900">Sample Product {item}</div>
                    <div className="text-gray-600">Keystone</div>
                    <div className="text-gray-900">250</div>
                    <div className="text-gray-600">2 hours ago</div>
                    <div><span className="px-2 py-1 text-xs font-medium rounded-full border bg-emerald-50 text-emerald-600 border-emerald-200">Active</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

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
                <button key={item.id} onClick={() => setActiveTab(item.id)} className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${activeTab===item.id ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>{item.icon}<span className="text-sm font-medium">{item.label}</span></button>
              ))}
            </div>
          </nav>
        </div>
        <div className="flex-1">
          <div className="bg-white shadow-sm border-b border-gray-200">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">{navigationItems.find(i=>i.id===activeTab)?.label || 'Dashboard'}</h1>
                  <p className="text-sm text-gray-500">Manage your supplier integrations and automation</p>
                </div>
                <div className="flex items-center space-x-4">
                  <button className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors"><Bell size={20}/><span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span></button>
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-full flex items-center justify-center"><Users className="h-4 w-4 text-white"/></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Admin User</p>
                      <p className="text-xs text-gray-500">System Administrator</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="p-6">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
