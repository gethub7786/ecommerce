import React, { useEffect, useState } from 'react'
import { listCatalog, deleteSku, deleteCatalogFile } from '../api/keystone'
import { RefreshCcw, Trash2, Upload, XCircle } from 'lucide-react'

export default function CatalogManager() {
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(0)
  const pageSize = 50
  const [hasNext,setHasNext]=useState(false)
  const [expanded, setExpanded] = useState<any | null>(null)

  const load = (p:number=0) => {
    setLoading(true);
    listCatalog({ params: { limit: pageSize+1, start: p*pageSize } })
      .then((r)=>{
        const data=r.data.rows||[];
        setHasNext(data.length>pageSize);
        setRows(data.slice(0,pageSize));
      })
      .finally(()=>setLoading(false))
  }
  useEffect(() => {
    load(0)
  }, [])

  const nextPage=()=>{ if(hasNext){ const np=page+1; setPage(np); load(np)} }
  const prevPage=()=>{ if(page>0){ const np=page-1; setPage(np); load(np)} }

  const qtyFields = [
    'EastQty','MidwestQty','CaliforniaQty','SoutheastQty','PacificNWQty','TexasQty','GreatLakesQty','FloridaQty','TexasDFWQty','TotalQty'
  ]

  const first50 = rows.slice(0,50)

  const getTotal = (r:any)=>{
    let total=0
    qtyFields.forEach(f=>{const v=parseInt(r[f]||'0',10); if(!isNaN(v)) total+=v})
    return total
  }

  const imageUrl = (r:any)=> {
    const keys = ['Image','ImageURL','IMAGEURL','image','image_url','Thumb','Thumbnail','ThumbURL']
    for(const k of keys){ if(r[k]) return String(r[k]) }
    return ''
  }

  return (
    <div className="space-y-4">
      <button
        onClick={()=>load(page)}
        className="flex items-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
      >
        <RefreshCcw className="h-4 w-4" /> Refresh
      </button>

      {loading && <p className="text-sm text-gray-500">Loading catalog…</p>}

      <div className="overflow-x-auto rounded border border-gray-200 bg-white shadow">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-left font-semibold text-gray-700">
            <tr>
              <th className="px-4 py-2">SKU</th>
              <th className="px-4 py-2">Brand</th>
              <th className="px-4 py-2">Title</th>
              <th className="px-4 py-2 text-right">Total Qty</th>
              <th className="px-4 py-2">Image</th>
              <th className="w-10"></th>
            </tr>
          </thead>
          <tbody>
            {first50.map((r, i) => {
              const sku = r.VCPN || r.SKU || r['AMAZON SKU']
              const isOpen = expanded===i
              return (
                <React.Fragment key={i}>
                  <tr className={`border-t border-gray-200 hover:bg-gray-50 ${isOpen?'bg-blue-50':''}`} onClick={()=>setExpanded(isOpen?null:i)}>
                    <td className="px-4 py-2 whitespace-nowrap font-medium text-gray-900">{sku}</td>
                    <td className="px-4 py-2">{r.VendorName}</td>
                    <td className="px-4 py-2 truncate max-w-xs">{r.LongDescription}</td>
                    <td className="px-4 py-2 text-right">{getTotal(r)}</td>
                    <td className="px-4 py-2">
                      {imageUrl(r) ? (
                        <img
                          src={imageUrl(r).replace('http://','https://')}
                          alt="img"
                          className="h-10 w-10 object-cover rounded"
                          onError={(e)=>{(e.currentTarget as HTMLImageElement).src='https://via.placeholder.com/40x40?text=NA'}}
                        />
                      ) : (
                        <span className="text-xs text-gray-400">N/A</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-right">
                      <button onClick={(e)=>{e.stopPropagation(); deleteSku(sku); load()}} className="rounded p-1 text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4"/></button>
                    </td>
                  </tr>
                  {isOpen && (
                    <tr className="border-t border-gray-100 bg-blue-50">
                      <td colSpan={6} className="p-4">
                        <div className="flex justify-between items-start">
                          <h4 className="font-semibold text-gray-900">Details</h4>
                          <button onClick={()=>setExpanded(null)} className="text-gray-500 hover:text-gray-700"><XCircle className="h-5 w-5"/></button>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 text-sm">
                          {Object.entries(r).map(([k,v])=> (
                            <div key={k} className="break-words">
                              <span className="font-medium">{k}:</span> {String(v)}
                            </div>
                          ))}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
            {first50.length===0 && (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-500">No data</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-2">
        <button onClick={prevPage} disabled={page===0 || loading} className="px-3 py-1 rounded bg-gray-200 text-sm disabled:opacity-50">Prev</button>
        <span className="text-sm text-gray-600">Page {page+1}</span>
        <button onClick={nextPage} disabled={!hasNext || loading} className="px-3 py-1 rounded bg-gray-200 text-sm disabled:opacity-50">Next</button>
      </div>


    </div>
  )
}
