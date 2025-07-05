import axios from 'axios'

axios.defaults.withCredentials = true

export function saveCredentials(feedId: string) {
  return axios.post('/cwr/credentials', { feed_id: feedId })
}

export function getCredentials() { return axios.get('/cwr/credentials') }

export function saveFtp(user: string, password: string, port: string | number = 22) {
  return axios.post('/cwr/ftp', { user, password, port })
}

export function saveSkuMap(path: string) {
  return axios.post('/cwr/sku-map', { path })
}

export function saveLocationMap(map: Record<string,string>) {
  return axios.post('/cwr/location-map', map)
}

export function schedulePartial(minutes: number) {
  return axios.post('/cwr/schedule/partial', { interval: minutes })
}
export function scheduleFull(minutes: number) {
  return axios.post('/cwr/schedule/full', { interval: minutes })
}
export function scheduleCatalog(minutes: number) {
  return axios.post('/cwr/schedule/catalog', { interval: minutes })
}

export function listCatalog() { return axios.get('/cwr/catalog') }
export function deleteSku(sku: string) { return axios.delete(`/cwr/catalog/${sku}`) }
export function deleteCatalogFile(path: string) { return axios.post('/cwr/catalog/delete-file', { path }) }
export function uploadMLI() { return axios.get('/cwr/upload-mli') }

export function runPartialInventory() { return axios.get('/cwr/inventory/partial') }
export function runFullInventory() { return axios.get('/cwr/inventory/full') }
export function runFTPFull() { return axios.get('/cwr/inventory/force-full') }
export function runCatalog() { return axios.get('/cwr/catalog/run') }
export function testConnection() { return axios.get('/cwr/test') } 