import axios from 'axios'

axios.defaults.withCredentials = true

export function fetchSeawideCatalogOverview() {
  return axios.get('/seawide/catalog/overview')
}

export function fetchSeawideCatalogRows(params: { start?: number; limit?: number; q?: string; brand?: string; supplier?: string }) {
  return axios.get('/seawide/catalog/rows', { params })
}

export function fetchSeawideCatalogFilters() {
  return axios.get('/seawide/catalog/filters')
}
