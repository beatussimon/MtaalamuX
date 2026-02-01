import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, User } from 'lucide-react'
import { messageService } from '../services/api'
import { useAuthStore } from '../store'

function MessagesPage() {
  const { user } = useAuthStore()
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState(null)
  const [newMessage, setNewMessage] = useState('')

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await messageService.getInbox()
        setMessages(response.data.results || response.data)
      } catch (error) {
        console.error('Failed to fetch messages:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchMessages()
  }, [])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return
    try {
      await messageService.send({ recipient: selectedUser, content: newMessage })
      setNewMessage('')
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-[calc(100vh-12rem)]">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Messages</h1>
      
      <div className="card h-full flex">
        <div className="w-1/3 border-r border-gray-200 dark:border-dark-700 p-4 overflow-y-auto">
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center space-x-3 animate-pulse">
                  <div className="w-12 h-12 bg-gray-200 dark:bg-dark-700 rounded-full" />
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 dark:bg-dark-700 rounded w-3/4 mb-2" />
                    <div className="h-3 bg-gray-200 dark:bg-dark-700 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : messages.length > 0 ? (
            messages.map((msg) => (
              <div
                key={msg.id}
                onClick={() => setSelectedUser(msg.sender?.id)}
                className={`flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedUser === msg.sender?.id ? 'bg-primary-50 dark:bg-primary-900/20' : 'hover:bg-gray-50 dark:hover:bg-dark-700'
                }`}
              >
                <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <User className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 dark:text-white truncate">{msg.sender?.username}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{msg.content}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">No messages yet</p>
          )}
        </div>
        
        <div className="flex-1 flex flex-col">
          {selectedUser ? (
            <>
              <div className="flex-1 p-4 overflow-y-auto">
                <p className="text-center text-gray-500 dark:text-gray-400">Select a conversation</p>
              </div>
              <form onSubmit={handleSend} className="p-4 border-t border-gray-200 dark:border-dark-700">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="input flex-1"
                  />
                  <button type="submit" className="btn-primary">
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">Select a conversation to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default MessagesPage
