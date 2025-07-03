import React from 'react';
import { Button, Stack, Typography } from '@mui/material';

interface Props {
  onSelect: (name: string) => void;
}

const Home: React.FC<Props> = ({ onSelect }) => (
  <Stack spacing={2} alignItems="flex-start">
    <Typography variant="h4">Suppliers</Typography>
    <Button variant="contained" onClick={() => onSelect('keystone')}>Keystone Automotive</Button>
    <Button variant="contained" onClick={() => onSelect('cwr')}>CWR Distribution</Button>
    <Button variant="contained" onClick={() => onSelect('seawide')}>Seawide</Button>
  </Stack>
);

export default Home;
