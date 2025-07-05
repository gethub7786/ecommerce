import React from 'react';
import { ShoppingCart } from 'lucide-react';

export default function AmazonInventoryPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="flex items-center gap-3 mb-4">
        <ShoppingCart size={40} className="text-blue-500" />
        <h2 className="text-3xl font-bold text-gray-900">Amazon Inventory</h2>
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-xl px-8 py-6 flex flex-col items-center shadow-sm">
        <span className="text-5xl font-extrabold text-blue-400 mb-2 animate-bounce">🚀</span>
        <h3 className="text-xl font-semibold text-blue-700 mb-2">Coming Soon</h3>
        <p className="text-gray-600 text-center max-w-md">We're working hard to bring you Amazon Inventory integration. Stay tuned for a powerful, seamless experience to manage your Amazon stock right from this dashboard!</p>
      </div>
    </div>
  );
}
