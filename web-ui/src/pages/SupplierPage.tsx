import React, { useState } from 'react';
import axios from 'axios';
import { Stack, TextField, Button, Typography } from '@mui/material';

interface Props {
  name: string;
  onBack: () => void;
}

const SupplierPage: React.FC<Props> = ({ name, onBack }) => {
  const [account, setAccount] = useState('');
  const [key, setKey] = useState('');
  const [message, setMessage] = useState('');

  const saveCreds = async () => {
    try {
      await axios.post(`/api/suppliers/${name}/credentials`, { account_number: account, api_key: key });
      setMessage('Credentials saved');
    } catch (err) {
      setMessage('Error saving');
    }
  };

  const runUpdate = async () => {
    setMessage('Running inventory...');
    try {
      await axios.post(`/api/suppliers/${name}/inventory/update`);
      setMessage('Update complete');
    } catch (err) {
      setMessage('Error running inventory');
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="h5">{name} Settings</Typography>
      <TextField label="Account Number" value={account} onChange={e => setAccount(e.target.value)} />
      <TextField label="API Key" value={key} onChange={e => setKey(e.target.value)} />
      <Button variant="contained" onClick={saveCreds}>Save Credentials</Button>
      <Button variant="outlined" onClick={runUpdate}>Run Inventory Update</Button>
      <Button onClick={onBack}>Back</Button>
      {message && <Typography>{message}</Typography>}
    </Stack>
  );
};

export default SupplierPage;
