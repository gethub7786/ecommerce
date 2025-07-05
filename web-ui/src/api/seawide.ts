import axios from 'axios'

axios.defaults.withCredentials = true

export function saveCredentials(account: string, apiKey: string) {
  return axios.post('/seawide/credentials', { account_number: account, api_key: apiKey })
}

export function getCredentials() { return axios.get('/seawide/credentials') }

export function saveFtp(user: string, password: string, remote_dir: string, remote_file: string) {
  return axios.post('/seawide/ftp', { user, password, remote_dir, remote_file })
}

export function getFtp() {
  return axios.get('/seawide/ftp')
}

export function saveLocationMap(map: Record<string,string>) {
  return axios.post('/seawide/location-map', map)
}

export function getLocationMap() {
  return axios.get('/seawide/location-map')
}

export function schedulePartial(minutes: number) {
  return axios.post('/seawide/schedule/partial', { interval: minutes })
}
export function scheduleFull(minutes: number) {
  return axios.post('/seawide/schedule/full', { interval: minutes })
}
export function scheduleCatalog(minutes: number) {
  return axios.post('/seawide/schedule/catalog', { interval: minutes })
}

export function getPartialSchedule() { return axios.get('/seawide/schedule/partial') }
export function getFullSchedule() { return axios.get('/seawide/schedule/full') }
export function getCatalogSchedule() { return axios.get('/seawide/schedule/catalog') }

export function listCatalog() { return axios.get('/seawide/catalog') }
export function deleteSku(sku: string) { return axios.delete(`/seawide/catalog/${sku}`) }
export function deleteCatalogFile(path: string) { return axios.post('/seawide/catalog/delete-file', { path }) }
export function uploadMLI() { return axios.get('/seawide/upload-mli') }

export function runPartialInventory() { return axios.get('/seawide/inventory/partial') }
export function runFullInventory() { return axios.get('/seawide/inventory/full') }
export function runFTPFull() { return axios.get('/seawide/inventory/ftp-full') }
export function runCatalog() { return axios.get('/seawide/catalog/run') }
export function testConnection() { return axios.get('/seawide/test') }

export function fetchCatalogOverview() {
  return axios.get('/seawide/catalog/overview')
}

export function fetchCatalogRows(params: { start?: number; limit?: number; q?: string; brand?: string; supplier?: string }) {
  return axios.get('/seawide/catalog/rows', { params })
}

export function fetchCatalogFilters() {
  return axios.get('/seawide/catalog/filters')
}