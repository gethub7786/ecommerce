import React, { useEffect, useState } from 'react'
import { fetchCatalogOverview as fetchKeystoneOverview, fetchCatalogRows as fetchKeystoneRows, fetchCatalogFilters as fetchKeystoneFilters } from '../api/keystone'
import { fetchCatalogOverview as fetchSeawideOverview, fetchCatalogRows as fetchSeawideRows, fetchCatalogFilters as fetchSeawideFilters } from '../api/seawide'
import { RefreshCcw, Search, ChevronLeft, ChevronRight } from 'lucide-react'
import Spinner from '../components/Spinner'

interface Row { sku:string; name:string; supplier:string; brand:string; stock:number; status:string }

export default function CatalogPage(){
  const pageSize=50
  const [overview,setOverview]=useState<any[]>([])
  const [rows,setRows]=useState<Row[]>([])
  const [page,setPage]=useState(0)
  const [hasNext,setHasNext]=useState(false)
  const [loading,setLoading]=useState(false)
  const [q,setQ]=useState('')
  const [brand,setBrand]=useState('')
  const [supplier,setSupplier]=useState('')
  const [brands,setBrands]=useState<string[]>([])
  const [suppliers,setSuppliers]=useState<string[]>([])
  const [filtersLoading, setFiltersLoading] = useState(false)

  useEffect(()=>{
    Promise.all([
      fetchKeystoneOverview(),
      fetchSeawideOverview()
    ]).then(([k,s])=>{
      setOverview([...(k.data.overview||[]), ...(s.data.overview||[])]);
    })
    setFiltersLoading(true)
    Promise.all([
      fetchKeystoneFilters(),
      fetchSeawideFilters()
    ]).then(([k,s])=>{
      setBrands([...(k.data.brands||[]), ...(s.data.brands||[])]);
      setSuppliers([...(k.data.suppliers||[]), ...(s.data.suppliers||[])]);
    }).finally(()=>setFiltersLoading(false))
    load(0)
  },[])

  useEffect(()=>{ load(0) },[q,brand,supplier])

  const load=(p:number)=>{
    setLoading(true)
    Promise.all([
      fetchKeystoneRows({start:p*pageSize,limit:pageSize+1,q,brand,supplier}),
      fetchSeawideRows({start:p*pageSize,limit:pageSize+1,q,brand,supplier})
    ]).then(([k,s])=>{
      const data=[...(k.data.rows||[]), ...(s.data.rows||[])]
      setHasNext(data.length>pageSize)
      setRows(data.slice(0,pageSize))
      setPage(p)
    }).finally(()=>setLoading(false))
  }

  const summaryCard=(title:string,value:any,sub?:string)=> (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Catalog Overview</h2>
        <button onClick={()=>{
          Promise.all([
            fetchKeystoneOverview(),
            fetchSeawideOverview()
          ]).then(([k,s])=>{
            setOverview([...(k.data.overview||[]), ...(s.data.overview||[])]);
          })
          setFiltersLoading(true)
          Promise.all([
            fetchKeystoneFilters(),
            fetchSeawideFilters()
          ]).then(([k,s])=>{
            setBrands([...(k.data.brands||[]), ...(s.data.brands||[])]);
            setSuppliers([...(k.data.suppliers||[]), ...(s.data.suppliers||[])]);
          }).finally(()=>setFiltersLoading(false))
          load(0)
        }} className="flex items-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"><RefreshCcw className="h-4 w-4"/> Refresh</button>
      </div>
      {/* summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {overview.map(o=>summaryCard(`${o.supplier} Active SKUs`,o.active,`Updated ${o.last_updated}`))}
      </div>

      {/* filters card */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 flex flex-col md:flex-row md:items-end gap-4">
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1">Search</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16}/>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search SKUs..." className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"/>
          </div>
        </div>
        <div className="w-full md:w-56">
          <label className="block text-xs text-gray-500 mb-1">Brand</label>
          <div className="relative">
            <select value={brand} onChange={e=>setBrand(e.target.value)} className="w-full border border-gray-300 rounded px-2 py-2 appearance-none pr-8">
              <option value="">All</option>
              {filtersLoading ? <option disabled>Loading…</option> : brands.map(b=>(<option key={b} value={b}>{b}</option>))}
            </select>
            {filtersLoading && <span className="absolute right-2 top-1/2 -translate-y-1/2"><Spinner className="w-4 h-4"/></span>}
          </div>
        </div>
        <div className="w-full md:w-56">
          <label className="block text-xs text-gray-500 mb-1">Supplier</label>
          <div className="relative">
            <select value={supplier} onChange={e=>setSupplier(e.target.value)} className="w-full border border-gray-300 rounded px-2 py-2 appearance-none pr-8">
              <option value="">All</option>
              {filtersLoading ? <option disabled>Loading…</option> : suppliers.map(s=>(<option key={s} value={s}>{s}</option>))}
            </select>
            {filtersLoading && <span className="absolute right-2 top-1/2 -translate-y-1/2"><Spinner className="w-4 h-4"/></span>}
          </div>
        </div>
      </div>

      {/* table */}
      {loading? <p className="text-sm text-gray-500 flex items-center gap-2"><Spinner/> Loading…</p> : (
      <div className="overflow-x-auto rounded border border-gray-200 bg-white shadow">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-left font-semibold text-gray-700">
            <tr>
              <th className="px-4 py-2">SKU</th><th className="px-4 py-2">Product Name</th><th className="px-4 py-2">Supplier</th><th className="px-4 py-2">Brand</th><th className="px-4 py-2 text-right">Stock</th><th className="px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r,i)=>(
              <tr key={i} className="border-t border-gray-200 hover:bg-gray-50">
                <td className="px-4 py-2 whitespace-nowrap font-medium">{r.sku}</td>
                <td className="px-4 py-2 truncate max-w-xs">{r.name}</td>
                <td className="px-4 py-2">{r.supplier}</td>
                <td className="px-4 py-2">{r.brand}</td>
                <td className="px-4 py-2 text-right">{r.stock}</td>
                <td className="px-4 py-2">{r.status}</td>
              </tr>
            ))}
            {rows.length===0 && (<tr><td colSpan={6} className="px-4 py-6 text-center text-gray-500">No rows</td></tr>)}
          </tbody>
        </table>
      </div>) }

      {/* pagination */}
      <div className="flex justify-between items-center mt-2">
        <button onClick={()=>load(Math.max(page-1,0))} disabled={page===0||loading} className="px-3 py-1 rounded bg-gray-200 text-sm disabled:opacity-50 flex items-center gap-1"><ChevronLeft size={14}/> Prev</button>
        <span className="text-sm text-gray-600">Page {page+1}</span>
        <button onClick={()=>{if(hasNext) load(page+1)}} disabled={!hasNext||loading} className="px-3 py-1 rounded bg-gray-200 text-sm disabled:opacity-50 flex items-center gap-1">Next <ChevronRight size={14}/></button>
      </div>
    </div>
  )
}