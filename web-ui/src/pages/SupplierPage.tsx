import React, { useState } from 'react';
import axios from 'axios';
import { Stack, TextField, Button, Typography } from '@mui/material';

interface Props {
  name: string;
  onBack: () => void;
}

const capabilities: Record<string, { skuMap?: boolean; catalog?: boolean }> = {
  cwr: { skuMap: true, catalog: true },
  keystone: {},
  seawide: {},
};

const SupplierPage: React.FC<Props> = ({ name, onBack }) => {
  const [account, setAccount] = useState('');
  const [key, setKey] = useState('');
  const [ftpUser, setFtpUser] = useState('');
  const [ftpPass, setFtpPass] = useState('');
  const [ftpDir, setFtpDir] = useState('/');
  const [ftpFile, setFtpFile] = useState('Inventory.csv');
  const [locMap, setLocMap] = useState('{}');
  const [skuMap, setSkuMap] = useState('');
  const [message, setMessage] = useState('');

  const saveCreds = async () => {
    try {
      await axios.post(`/api/${name}/set-credentials`, {
        account_number: account,
        api_key: key,
        feed_id: account,
      });
      setMessage('Credentials saved');
    } catch {
      setMessage('Error saving');
    }
  };

  const saveFtp = async () => {
    try {
      await axios.post(`/api/${name}/set-ftp`, {
        ftp_user: ftpUser,
        ftp_password: ftpPass,
        ftp_remote_dir: ftpDir,
        remote_update_file: ftpFile,
      });
      setMessage('FTP saved');
    } catch {
      setMessage('FTP error');
    }
  };

  const saveLocMap = async () => {
    try {
      await axios.post(`/api/${name}/location-map`, JSON.parse(locMap));
      setMessage('Mapping saved');
    } catch {
      setMessage('Map error');
    }
  };

  const saveSkuMap = async () => {
    try {
      await axios.post(`/api/${name}/sku-map`, { path: skuMap });
      setMessage('SKU map saved');
    } catch {
      setMessage('Map error');
    }
  };

  const runPartial = async () => {
    setMessage('Running partial inventory...');
    try {
      await axios.post(`/api/${name}/inventory/partial`);
      setMessage('Done');
    } catch {
      setMessage('Error');
    }
  };

  const runFull = async () => {
    setMessage('Running full inventory...');
    try {
      await axios.post(`/api/${name}/inventory/full`);
      setMessage('Done');
    } catch {
      setMessage('Error');
    }
  };

  const runMulti = async () => {
    setMessage('Converting...');
    try {
      await axios.post(`/api/${name}/multi-location`);
      setMessage('Done');
    } catch {
      setMessage('Error');
    }
  };

  const runCatalog = async () => {
    setMessage('Downloading catalog...');
    try {
      await axios.post(`/api/${name}/catalog`);
      setMessage('Done');
    } catch {
      setMessage('Error');
    }
  };

  const runTest = async () => {
    setMessage('Testing...');
    try {
      await axios.get(`/api/${name}/test`);
      setMessage('Connection OK');
    } catch {
      setMessage('Failed');
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="h5">{name} Settings</Typography>
      <TextField label="Account/Feed ID" value={account} onChange={e => setAccount(e.target.value)} />
      <TextField label="API/Security Key" value={key} onChange={e => setKey(e.target.value)} />
      <Button variant="contained" onClick={saveCreds}>Save Credentials</Button>

      <TextField label="FTP User" value={ftpUser} onChange={e => setFtpUser(e.target.value)} />
      <TextField label="FTP Password" type="password" value={ftpPass} onChange={e => setFtpPass(e.target.value)} />
      <TextField label="Remote Folder" value={ftpDir} onChange={e => setFtpDir(e.target.value)} />
      <TextField label="Remote File" value={ftpFile} onChange={e => setFtpFile(e.target.value)} />
      <Button variant="contained" onClick={saveFtp}>Save FTP</Button>

      <TextField label="Location Mapping (JSON)" value={locMap} onChange={e => setLocMap(e.target.value)} />
      <Button variant="contained" onClick={saveLocMap}>Save Location Map</Button>

      {capabilities[name]?.skuMap && (
        <>
          <TextField label="SKU Mapping File" value={skuMap} onChange={e => setSkuMap(e.target.value)} />
          <Button variant="contained" onClick={saveSkuMap}>Save SKU Mapping</Button>
        </>
      )}

      <Button variant="outlined" onClick={runPartial}>Run Partial Inventory</Button>
      <Button variant="outlined" onClick={runFull}>Run Full Inventory</Button>
      {capabilities[name]?.catalog && (
        <Button variant="outlined" onClick={runCatalog}>Download Catalog</Button>
      )}
      <Button variant="outlined" onClick={runMulti}>Upload Multi-location</Button>
      <Button variant="outlined" onClick={runTest}>Test Connection</Button>
      <Button onClick={onBack}>Back</Button>
      {message && <Typography>{message}</Typography>}
    </Stack>
  );
};

export default SupplierPage;
