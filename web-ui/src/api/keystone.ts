import axios from 'axios'

axios.defaults.withCredentials = true

export function saveCredentials(account: string, key: string) {
  return axios.post('/keystone/credentials', { account_number: account, security_key: key })
}

export function getCredentials() {
  return axios.get('/keystone/credentials')
}

export function saveFtp(user: string, password: string, remote_dir: string, remote_file: string) {
  return axios.post('/keystone/ftp', { user, password, remote_dir, remote_file })
}

// Retrieve saved FTP credentials
export function getFtp() {
  return axios.get('/keystone/ftp')
}

export function saveLocationMap(map: Record<string,string>) {
  return axios.post('/keystone/location-map', map)
}

// Retrieve saved location mapping
export function getLocationMap() {
  return axios.get('/keystone/location-map')
}

export function schedulePartial(minutes: number) {
  return axios.post('/keystone/schedule/partial', { interval: minutes })
}

export function getPartialSchedule() {
  return axios.get('/keystone/schedule/partial')
}
export function scheduleFull(minutes: number) {
  return axios.post('/keystone/schedule/full', { interval: minutes })
}

export function getFullSchedule() {
  return axios.get('/keystone/schedule/full')
}
export function scheduleCatalog(minutes: number) {
  return axios.post('/keystone/schedule/catalog', { interval: minutes })
}

export function getCatalogSchedule() {
  return axios.get('/keystone/schedule/catalog')
}

export function listCatalog(config?: any) { return axios.get('/keystone/catalog', config) }

// new aggregated catalog endpoints
export function fetchCatalogOverview(){ return axios.get('/catalog/overview') }
/**
 * Fetch catalog rows with optional filters.
 * @param params {q?:string, start?:number, limit?:number, brand?:string, supplier?:string}
 */
export function fetchCatalogRows(params:any){ return axios.get('/catalog/rows', { params }) }
export function deleteSku(sku: string) { return axios.delete(`/keystone/catalog/${sku}`) }
export function deleteCatalogFile(path: string) { return axios.post('/keystone/catalog/delete-file', { path }) }
export function uploadMLI() { return axios.get('/keystone/upload-mli') }

export function runPartialInventory() { return axios.get('/keystone/inventory/partial') }
export function runFullInventory() { return axios.get('/keystone/inventory/full') }
export function runFTPFull() { return axios.get('/keystone/inventory/ftp-full') }
export function runCatalog() { return axios.get('/keystone/catalog/run') }
export function testConnection() { return axios.get('/keystone/test') }

export function fetchSupplierStatus() {
  return axios.get('/suppliers/status')
}

export function fetchTasks() {
  return axios.get(`/tasks?_=${Date.now()}`)
}

export function fetchCatalogFilters() { return axios.get('/catalog/filters') }
