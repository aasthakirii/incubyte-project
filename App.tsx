import { useEffect, useMemo, useState } from 'react'
import { CarFront, Search, LogOut, Plus, SlidersHorizontal, Gauge, ShieldCheck, CheckCircle2 } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
type Vehicle = { id: number; make: string; model: string; category: string; price: number; quantity: number }
type User = { email: string; is_admin: boolean }
type Draft = Omit<Vehicle, 'id'>

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [user, setUser] = useState<User | null>(null)
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [registerMode, setRegisterMode] = useState(false)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All categories')
  const [maxPrice, setMaxPrice] = useState('')
  const [notice, setNotice] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [draft, setDraft] = useState<Draft>({ make: '', model: '', category: 'SUV', price: 25000, quantity: 1 })

  async function request(path: string, options: RequestInit = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) },
    })
    const body = response.status === 204 ? null : await response.json().catch(() => null)
    if (!response.ok) throw new Error(body?.detail || 'Something went wrong')
    return body
  }
  async function loadVehicles() {
    try {
      const params = new URLSearchParams()
      if (query.trim()) params.set('q', query.trim())
      if (category !== 'All categories') params.set('category', category)
      if (maxPrice) params.set('max_price', maxPrice)
      const path = query.trim() || category !== 'All categories' || maxPrice
        ? `/api/vehicles/search?${new URLSearchParams({ ...(query.trim() ? { make: query.trim() } : {}), ...(category !== 'All categories' ? { category } : {}), ...(maxPrice ? { max_price: maxPrice } : {}) })}`
        : '/api/vehicles'
      setVehicles(await request(path))
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load inventory') }
  }
  useEffect(() => {
    if (!token) return
    request('/api/auth/me').then(setUser).then(loadVehicles).catch(() => { localStorage.removeItem('token'); setToken('') })
  }, [token])
  useEffect(() => { if (token) loadVehicles() }, [query, category, maxPrice])
  async function authenticate(event: React.FormEvent) {
    event.preventDefault()
    try {
      if (registerMode) await request('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) })
      const result = await request('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
      localStorage.setItem('token', result.access_token); setToken(result.access_token); setNotice('Welcome to Motorhaus.')
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Authentication failed') }
  }
  async function purchase(vehicle: Vehicle) {
    try { await request(`/api/vehicles/${vehicle.id}/purchase`, { method: 'POST' }); setNotice(`${vehicle.make} ${vehicle.model} purchase recorded.`); await loadVehicles() }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Purchase failed') }
  }
  async function addVehicle(event: React.FormEvent) {
    event.preventDefault()
    try { await request('/api/vehicles', { method: 'POST', body: JSON.stringify(draft) }); setShowForm(false); setNotice('Vehicle added to inventory.'); await loadVehicles() }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Could not add vehicle') }
  }
  async function restock(vehicle: Vehicle) {
    const raw = window.prompt(`How many ${vehicle.make} ${vehicle.model} units should be added?`, '1')
    if (raw === null) return
    const quantity = Number(raw)
    if (!Number.isInteger(quantity) || quantity < 1) { setNotice('Enter a whole number greater than zero.'); return }
    try { await request(`/api/vehicles/${vehicle.id}/restock`, { method: 'POST', body: JSON.stringify({ quantity }) }); setNotice('Stock updated.'); await loadVehicles() }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Restock failed') }
  }
  async function editVehicle(vehicle: Vehicle) {
    const raw = window.prompt('Enter the new price:', String(vehicle.price))
    if (raw === null) return
    const price = Number(raw)
    if (!Number.isFinite(price) || price < 0) { setNotice('Enter a valid non-negative price.'); return }
    try { await request(`/api/vehicles/${vehicle.id}`, { method: 'PUT', body: JSON.stringify({ price }) }); setNotice('Vehicle updated.'); await loadVehicles() }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Update failed') }
  }
  async function deleteVehicle(vehicle: Vehicle) {
    if (!window.confirm(`Delete ${vehicle.make} ${vehicle.model} from inventory?`)) return
    try { await request(`/api/vehicles/${vehicle.id}`, { method: 'DELETE' }); setNotice('Vehicle deleted.'); await loadVehicles() }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Delete failed') }
  }
  function logout() { localStorage.removeItem('token'); setToken(''); setUser(null); setVehicles([]) }
  const totalUnits = useMemo(() => vehicles.reduce((sum, v) => sum + v.quantity, 0), [vehicles])
  if (!token) return <main className="auth-shell"><div className="auth-card"><div className="brand-mark"><CarFront size={28}/></div><p className="eyebrow">THE MODERN MOTOR EXPERIENCE</p><h1>Find your<br/><em>next drive.</em></h1><p className="muted">Sign in to explore the curated inventory and manage your showroom.</p><form onSubmit={authenticate} className="auth-form"><label>Email address<input type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></label><label>Password<input type="password" minLength={registerMode ? 8 : 1} required value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 8 characters"/></label><button className="primary full" type="submit">{registerMode ? 'Create account' : 'Sign in'} <span>↗</span></button></form><button className="text-button" onClick={()=>setRegisterMode(!registerMode)}>{registerMode ? 'Already registered? Sign in' : 'New here? Create an account'}</button>{notice && <p className="notice">{notice}</p>}<p className="tiny">SECURE ACCESS · INVENTORY CONTROL</p></div><div className="auth-art"><div className="art-copy"><span>01 / DISCOVER</span><h2>Designed for<br/>the road ahead.</h2><p>A considered collection of vehicles, built around your next chapter.</p></div><div className="art-car"><CarFront size={190} strokeWidth={0.7}/></div><div className="art-footer"><span>CURATED INVENTORY</span><span>EST. 2025</span></div></div></main>
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><span className="brand-mark small"><CarFront size={20}/></span><span>MOTORHAUS<small>INVENTORY STUDIO</small></span></div><div className="side-label">WORKSPACE</div><div className="nav-active"><Gauge size={17}/> Inventory <span className="nav-count">{vehicles.length}</span></div><div className="side-label account-label">ACCOUNT</div><div className="profile"><div className="avatar">{user?.email?.slice(0,1).toUpperCase() || 'U'}</div><div className="profile-copy"><b>{user?.email || 'Member'}</b><span>{user?.is_admin ? 'Administrator' : 'Customer account'}</span></div></div><button className="logout" onClick={logout}><LogOut size={16}/> Sign out</button><div className="sidebar-bottom"><ShieldCheck size={16}/><span>Secure inventory<br/>management</span></div></aside><main className="main-area"><header className="topbar"><div><span className="breadcrumb">WORKSPACE /</span> <b>Inventory</b></div><div className="top-status"><span className="status-dot"></span> System operational <span className="top-divider"></span> <span>2026 EDITION</span></div></header><section className="page-content"><div className="hero-row"><div><p className="eyebrow">YOUR SHOWROOM AT A GLANCE</p><h1>Vehicle <em>inventory.</em></h1><p className="muted">Discover the collection. Find the right fit.</p></div>{user?.is_admin && <button className="primary add-button" onClick={()=>setShowForm(!showForm)}><Plus size={17}/> Add vehicle</button>}</div><div className="metrics"><div className="metric"><span className="metric-label">LISTED VEHICLES</span><b>{vehicles.length.toString().padStart(2,'0')}</b><span className="metric-foot">Unique models in view</span></div><div className="metric"><span className="metric-label">UNITS IN STOCK</span><b>{totalUnits.toString().padStart(2,'0')}</b><span className="metric-foot"><span className="status-dot"/> Ready for purchase</span></div><div className="metric"><span className="metric-label">COLLECTION STATUS</span><b className="live-label">Live <CheckCircle2 size={18}/></b><span className="metric-foot">Inventory synced to API</span></div></div>{showForm && user?.is_admin && <form className="vehicle-form" onSubmit={addVehicle}><h3>Add to collection</h3><div className="form-grid">{(['make','model','category','price','quantity'] as const).map(key=><label key={key}>{key}<input required type={key==='price'||key==='quantity'?'number':'text'} min={key==='price'||key==='quantity'?0:undefined} value={draft[key]} onChange={e=>setDraft({...draft,[key]:key==='price'||key==='quantity'?Number(e.target.value):e.target.value})}/></label>)}</div><button className="primary" type="submit">Save vehicle</button></form>}<div className="inventory-heading"><div><h2>The collection <span>{vehicles.length}</span></h2><p>Browse available vehicles in the showroom.</p></div><div className="collection-note"><span className="status-dot"/> UPDATED LIVE</div></div><div className="filters"><div className="search-box"><Search size={17}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search make or model..."/></div><div className="select-wrap"><SlidersHorizontal size={16}/><select value={category} onChange={e=>setCategory(e.target.value)}><option>All categories</option><option>SUV</option><option>Sedan</option><option>Hatchback</option><option>Coupe</option><option>Electric</option><option>Truck</option></select></div><div className="price-wrap"><span>MAX PRICE</span><input aria-label="Maximum price" type="number" min="0" placeholder="Any" value={maxPrice} onChange={e=>setMaxPrice(e.target.value)}/></div></div>{notice && <div className="notice-banner">{notice}<button onClick={()=>setNotice('')}>Dismiss</button></div>}{vehicles.length===0 ? <div className="empty"><CarFront size={36}/><h3>Your collection is waiting.</h3><p>No vehicles match these filters, or the inventory is empty.</p></div> : <div className="vehicle-grid">{vehicles.map((v,index)=><article className="vehicle-card" key={v.id}><div className={`vehicle-visual visual-${index%4}`}><span className="category-pill">{v.category}</span><span className="vehicle-number">MH / {String(v.id).padStart(3,'0')}</span><CarFront size={106} strokeWidth={0.8}/><div className="visual-caption">MOTORHAUS <span>COLLECTION</span></div></div><div className="vehicle-info"><div className="vehicle-meta"><span>{v.make.toUpperCase()}</span><span className={v.quantity>0?'in-stock':'out-stock'}>{v.quantity>0?'IN STOCK':'SOLD OUT'}</span></div><h3>{v.model}</h3><div className="vehicle-bottom"><div><span className="price-label">STARTING AT</span><b>${v.price.toLocaleString('en-US')}</b></div><button className="purchase" disabled={v.quantity===0} onClick={()=>purchase(v)}>{v.quantity===0?'Unavailable':'Purchase ↗'}</button></div>{user?.is_admin && <div className="admin-actions"><button onClick={()=>editVehicle(v)}>Edit price</button><button onClick={()=>restock(v)}>Restock</button><button onClick={()=>deleteVehicle(v)}>Delete</button></div>}<div className="stock-line"><span>Stock level</span><b>{v.quantity} unit{v.quantity===1?'':'s'}</b></div></div></article>)}</div>}<footer><span>© 2026 MOTORHAUS INVENTORY STUDIO</span><span>BUILT WITH PRECISION <span className="footer-dot">◆</span></span></footer></section></main></div>
}
