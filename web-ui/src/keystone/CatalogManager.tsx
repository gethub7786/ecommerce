import React, { useEffect, useState } from 'react'
import { Button, Stack, TextField, TableContainer, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material'
import { listCatalog, deleteSku, deleteCatalogFile } from '../api/keystone'

export default function CatalogManager() {
  const [rows, setRows] = useState<any[]>([])
  const [file, setFile] = useState('')
  const load = () => listCatalog().then(r=>setRows(r.data.rows || []))
  useEffect(()=>{load()},[])
  return (
    <Stack spacing={2}>
      <Button variant="contained" onClick={load}>Refresh</Button>
      <TableContainer>
        <Table size="small">
          <TableHead><TableRow><TableCell>SKU</TableCell><TableCell>DATA</TableCell><TableCell/></TableRow></TableHead>
          <TableBody>
            {rows.map((r,i)=>(
              <TableRow key={i}>
                <TableCell>{r.SKU || r['AMAZON SKU']}</TableCell>
                <TableCell>{r.DATA}</TableCell>
                <TableCell><Button onClick={()=>{deleteSku(r.SKU || r['AMAZON SKU']);load()}}>Delete</Button></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Stack direction="row" spacing={1}>
        <TextField label="Delete File" value={file} onChange={e=>setFile(e.target.value)} />
        <Button onClick={()=>{deleteCatalogFile(file);load()}}>Upload Delete File</Button>
      </Stack>
    </Stack>
  )
}
