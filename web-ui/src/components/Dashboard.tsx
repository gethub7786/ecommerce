import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1>Automation Tool Dashboard</h1>
      <p>Select a supplier to manage inventory tasks.</p>
      <div>
        <button>Keystone Automotive</button>
        <button>CWR Distribution</button>
        <button>Seawide</button>
      </div>
    </div>
  );
};

export default Dashboard;
