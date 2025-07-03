import React, { useState } from 'react';
import {
  ArrowLeft,
  CheckCircle,
  Plus,
  Save,
  Search,
  TestTube
} from 'lucide-react';

/* ────────────────────────────────────────────────────────────
   1.  Type Definitions
   ──────────────────────────────────────────────────────────── */
interface PrebuiltIntegration {
  id: 'keystone' | 'cwr';
  name: string;
  icon: string;
  description: string;
  features: string[];
  isPopular?: boolean;
}

/* ────────────────────────────────────────────────────────────
   2.  Constants (Keystone & CWR only)
   ──────────────────────────────────────────────────────────── */
const prebuiltIntegrations: PrebuiltIntegration[] = [
  {
    id: 'keystone',
    name: 'Keystone Automotive',
    icon: '🔧',
    description:
      'Complete automotive parts integration with real-time inventory and catalog sync',
    features: [
      'Real-time inventory',
      'Catalog sync',
      'Multi-location support',
      'FTP backup'
    ],
    isPopular: true
  },
  {
    id: 'cwr',
    name: 'CWR Electronics',
    icon: '⚡',
    description:
      'Electronics components with advanced pricing and availability',
    features: [
      'Dynamic pricing',
      'Availability tracking',
      'Bulk updates',
      'API integration'
    ]
  }
];

/* ────────────────────────────────────────────────────────────
   3.  Main Component
   ──────────────────────────────────────────────────────────── */
const App: React.FC = () => {
  /* UI state */
  const [search, setSearch] = useState('');
  const [showGallery, setShowGallery] = useState(true);
  const [selected, setSelected] = useState<PrebuiltIntegration | null>(null);

  /* ── Handlers ───────────────────────────────────────────── */
  const openGallery = () => {
    setSelected(null);
    setShowGallery(true);
  };

  const openConfig = (intg: PrebuiltIntegration) => {
    setSelected(intg);
    setShowGallery(false);
  };

  const saveConfig = () => {
    console.log('Saving integration:', selected);
    // TODO: call backend POST /integrations
    openGallery();
  };

  /* ── Render: Gallery of Prebuilt Integrations ───────────── */
  const renderGallery = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <h2 className="text-2xl font-bold text-gray-900">Add Integration</h2>
        <p className="text-sm text-gray-500">
          Choose from our prebuilt supplier integrations
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          size={16}
        />
        <input
          type="text"
          placeholder="Search integrations…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-blue-500"
        />
      </div>

      {/* Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {prebuiltIntegrations
          .filter(i =>
            (i.name + i.description)
              .toLowerCase()
              .includes(search.toLowerCase())
          )
          .map(i => (
            <div
              key={i.id}
              onClick={() => openConfig(i)}
              className="bg-white border rounded-xl shadow-sm hover:shadow-md transition cursor-pointer relative"
            >
              {i.isPopular && (
                <div className="absolute -top-2 -right-2 bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
                  Popular
                </div>
              )}
              <div className="p-6 space-y-4">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{i.icon}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{i.name}</h3>
                    <p className="text-xs text-gray-500 capitalize">
                      {i.id} integration
                    </p>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{i.description}</p>
                <button
                  onClick={e => {
                    e.stopPropagation();
                    openConfig(i);
                  }}
                  className="w-full py-2 text-sm font-medium bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                >
                  Configure Integration
                </button>
              </div>
            </div>
          ))}
      </div>
    </div>
  );

  /* ── Render: Configuration Form ─────────────────────────── */
  const renderConfig = () => {
    if (!selected) return null;
    return (
      <div className="space-y-6">
        {/* Back */}
        <button
          onClick={openGallery}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft size={18} />
          <span>Back to gallery</span>
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3">
          <span className="text-4xl">{selected.icon}</span>
          <h2 className="text-2xl font-bold text-gray-900">
            Configure: {selected.name}
          </h2>
        </div>

        {/* Simple Form */}
        <div className="bg-white border rounded-xl shadow-sm p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <input
              type="password"
              placeholder="Enter API key"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Secret
            </label>
            <input
              type="password"
              placeholder="Enter API secret"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>

          {/* Features checklist */}
          <div>
            <h4 className="font-medium mb-2">Enable Features</h4>
            <div className="grid gap-2 md:grid-cols-2">
              {selected.features.map(f => (
                <label key={f} className="flex items-center space-x-2">
                  <input type="checkbox" defaultChecked />
                  <span className="text-sm">{f}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3">
            <button
              onClick={() => console.log('Test connection')}
              className="px-4 py-2 border rounded-lg flex items-center space-x-2"
            >
              <TestTube size={16} />
              <span>Test Connection</span>
            </button>
            <button
              onClick={saveConfig}
              className="px-5 py-2 bg-blue-600 text-white rounded-lg flex items-center space-x-2 hover:bg-blue-700"
            >
              <Save size={16} />
              <span>Save Integration</span>
            </button>
          </div>
        </div>
      </div>
    );
  };

  /* ── Main Render ─────────────────────────────────────────── */
  return (
    <div className="min-h-screen bg-slate-50 p-10">
      {showGallery ? renderGallery() : renderConfig()}
    </div>
  );
};

export default App;
