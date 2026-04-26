import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'

import {
  AgenticCustomerSupport,
  AdminDashboard,
  CustomerLookup,
  Home,
  ProtectedRoute,
  SignIn,
  SignUp

} from "./component"


const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index:true,
        element: <Home />

      },
      {
        path: "signIn",
        element: <SignIn />
      },
      {
        path: "signUp",
        element: <SignUp />
      },
      {
        path: "admin",
        element: (
          <ProtectedRoute requireAdmin>
            <AdminDashboard />
          </ProtectedRoute>
        )
      },
      {
        path: "customers",
        element: (
          <ProtectedRoute requireAdmin>
            <CustomerLookup />
          </ProtectedRoute>
        )
      }
    ]
  },
  {
    path: "/chat/:id",
    element: (
      <ProtectedRoute>
        <AgenticCustomerSupport />
      </ProtectedRoute>
    )
  },

])


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
