import axios from 'axios'

export function saveCredentials(account: string, key: string) {
  return axios.post('/keystone/credentials', { account_number: account, security_key: key })
}

export function saveFtp(user: string, password: string, remote_dir: string, remote_file: string) {
  return axios.post('/keystone/ftp', { user, password, remote_dir, remote_file })
}

export function saveLocationMap(map: Record<string,string>) {
  return axios.post('/keystone/location-map', map)
}

export function schedulePartial() { return axios.post('/keystone/schedule/partial') }
export function scheduleFull() { return axios.post('/keystone/schedule/full') }
export function scheduleCatalog() { return axios.post('/keystone/schedule/catalog') }

export function listCatalog() { return axios.get('/keystone/catalog') }
export function deleteSku(sku: string) { return axios.delete(`/keystone/catalog/${sku}`) }
export function deleteCatalogFile(path: string) { return axios.post('/keystone/catalog/delete-file', { path }) }
export function uploadMLI() { return axios.get('/keystone/upload-mli') }

export function runPartialInventory() { return axios.get('/keystone/inventory/partial') }
export function runFullInventory() { return axios.get('/keystone/inventory/full') }
export function runFTPFull() { return axios.get('/keystone/inventory/ftp-full') }
export function runCatalog() { return axios.get('/keystone/catalog/run') }
export function testConnection() { return axios.get('/keystone/test') }
