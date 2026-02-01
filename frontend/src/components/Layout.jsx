import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore, useThemeStore, useUIStore } from '../store'
import Header from './Header'
import Sidebar from './Sidebar'

function Layout() {
  const { sidebarOpen, closeSidebar } = useUIStore()
  const { isAuthenticated } = useAuthStore()
  const { theme } = useThemeStore()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900 transition-colors duration-300">
      {/* Header */}
      <Header />

      <div className="flex">
        {/* Sidebar - only show when authenticated */}
        {isAuthenticated && (
          <>
            {/* Mobile overlay */}
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                  onClick={closeSidebar}
                />
              )}
            </AnimatePresence>

            {/* Sidebar */}
            <motion.aside
              initial={false}
              animate={{ x: sidebarOpen ? 0 : '-100%' }}
              className="fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white dark:bg-dark-800 shadow-lg lg:shadow-none"
            >
              <Sidebar />
            </motion.aside>
          </>
        )}

        {/* Main content */}
        <main
          className={`flex-1 min-h-screen ${
            isAuthenticated ? 'lg:ml-0' : ''
          }`}
        >
          <div className="container mx-auto px-4 py-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
