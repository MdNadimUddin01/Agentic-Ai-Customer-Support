import { Outlet } from "react-router-dom"
import { Header } from "./component"

function App() {


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <Header />
      <Outlet/>
    </div>
  )
}

export default App
