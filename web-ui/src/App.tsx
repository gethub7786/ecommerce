import React, { useState } from 'react';
import { Container } from '@mui/material';
import Home from './pages/Home';
import SupplierPage from './pages/SupplierPage';

const App: React.FC = () => {
  const [supplier, setSupplier] = useState<string | null>(null);
  return (
    <Container sx={{ mt: 4 }}>
      {supplier ? (
        <SupplierPage name={supplier} onBack={() => setSupplier(null)} />
      ) : (
        <Home onSelect={name => setSupplier(name)} />
      )}
    </Container>
  );
};

export default App;
