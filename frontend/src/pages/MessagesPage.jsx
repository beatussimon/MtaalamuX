import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Send, User, Image, Paperclip, MoreVertical, Phone, Video, ArrowLeft } from 'lucide-react'
import { messageService, conversationService } from '../services/api'
import { useAuthStore, tierHelpers } from '../store'

function MessagesPage() {
  const { user, tierInfo } = useAuthStore()
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)
  
  const isProfessional = tierHelpers.isProfessional(tierInfo)
  const isPremium = tierHelpers.isPremium(tierInfo)

  const canMessage = isProfessional || isPremium

  useEffect(() => {
    fetchConversations()
  }, [])

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id)
    }
  }, [selectedConversation])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchConversations = async () => {
    try {
      setLoading(true)
      const response = await conversationService.getAll()
      setConversations(response.data.results || response.data || [])
      setError(null)
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
      setError('Failed to load conversations')
      // Set empty array to prevent further errors
      setConversations([])
    } finally {
      setLoading(false)
    }
  }

  const fetchMessages = async (conversationId) => {
    try {
      const response = await conversationService.getMessages(conversationId)
      setMessages(response.data.results || response.data || [])
      setError(null)
    } catch (error) {
      console.error('Failed to fetch messages:', error)
      setError('Failed to load messages')
      setMessages([])
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !selectedConversation) return

    try {
      setSending(true)
      const response = await messageService.send({
        conversation: selectedConversation.id,
        content: newMessage.trim()
      })
      
      // Add the new message to the list
      const sentMessage = response.data
      setMessages(prev => [...prev, sentMessage])
      setNewMessage('')
      setError(null)
    } catch (error) {
      console.error('Failed to send message:', error)
      setError('Failed to send message. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const getOtherParticipant = (conversation) => {
    if (!conversation.participants || conversation.participants.length === 0) return null
    return conversation.participants.find(p => p.id !== user?.id) || conversation.participants[0]
  }

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' })
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
  }

  // Show access denied message for basic users
  if (!canMessage) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="flex flex-col items-center justify-center h-[calc(100vh-12rem)]"
      >
        <div className="w-20 h-20 bg-gray-100 dark:bg-dark-800 rounded-full flex items-center justify-center mb-6">
          <User className="w-10 h-10 text-gray-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Messaging Unavailable
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-6">
          Messaging is available for Professional and Premium users only. 
          Upgrade your account to start messaging experts.
        </p>
        <a href="/upgrade" className="btn-primary">
          Upgrade to Professional
        </a>
      </motion.div>
    )
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="h-[calc(100vh-8rem)]"
    >
      <div className="card h-full flex overflow-hidden">
        {/* Conversations List */}
        <div className="w-80 border-r border-gray-200 dark:border-dark-700 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-dark-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Messages</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {conversations.length} conversations
            </p>
          </div>

          {/* Search/Filter */}
          <div className="p-4 border-b border-gray-200 dark:border-dark-700">
            <input
              type="text"
              placeholder="Search conversations..."
              className="input w-full"
            />
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="space-y-4 p-4">
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
            ) : error && !selectedConversation ? (
              <div className="p-4 text-center text-red-500">
                {error}
              </div>
            ) : conversations.length > 0 ? (
              conversations.map((conversation) => {
                const otherParticipant = getOtherParticipant(conversation)
                const lastMessage = conversation.last_message
                
                return (
                  <div
                    key={conversation.id}
                    onClick={() => setSelectedConversation(conversation)}
                    className={`flex items-center space-x-3 p-4 cursor-pointer transition-colors ${
                      selectedConversation?.id === conversation.id 
                        ? 'bg-primary-50 dark:bg-primary-900/20 border-r-2 border-primary-500' 
                        : 'hover:bg-gray-50 dark:hover:bg-dark-700'
                    }`}
                  >
                    <div className="relative">
                      <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center overflow-hidden">
                        {otherParticipant?.photo ? (
                          <img 
                            src={otherParticipant.photo} 
                            alt={otherParticipant.username}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <User className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        )}
                      </div>
                      {/* Online indicator */}
                      {otherParticipant?.is_online && (
                        <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-dark-800" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-gray-900 dark:text-white truncate">
                          {otherParticipant?.username || 'Unknown User'}
                        </p>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {lastMessage && formatMessageTime(lastMessage.created_at || lastMessage.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {lastMessage?.content || 'No messages yet'}
                      </p>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="p-8 text-center">
                <User className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">No conversations yet</p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                  Start a conversation by visiting a professional's profile
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedConversation ? (
            <>
              {/* Chat Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-700">
                <div className="flex items-center space-x-3">
                  <button 
                    onClick={() => setSelectedConversation(null)}
                    className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg"
                  >
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center overflow-hidden">
                    {getOtherParticipant(selectedConversation)?.photo ? (
                      <img 
                        src={getOtherParticipant(selectedConversation).photo} 
                        alt=""
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {getOtherParticipant(selectedConversation)?.username || 'Unknown User'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {getOtherParticipant(selectedConversation)?.is_online ? 'Online' : 'Offline'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg">
                    <Phone className="w-5 h-5 text-gray-500" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg">
                    <Video className="w-5 h-5 text-gray-500" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg">
                    <MoreVertical className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length > 0 ? (
                  messages.map((msg, index) => {
                    const isOwn = msg.sender?.id === user?.id
                    const showAvatar = !isOwn && (index === 0 || messages[index - 1]?.sender?.id !== msg.sender?.id)
                    
                    return (
                      <div
                        key={msg.id || index}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`flex items-end space-x-2 max-w-[70%] ${isOwn ? 'flex-row-reverse space-x-reverse' : ''}`}>
                          {showAvatar && !isOwn && (
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex-shrink-0 overflow-hidden">
                              {msg.sender?.photo ? (
                                <img 
                                  src={msg.sender.photo} 
                                  alt=""
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <User className="w-4 h-4 text-primary-600 dark:text-primary-400 mx-auto mt-2" />
                              )}
                            </div>
                          )}
                          {!showAvatar && !isOwn && <div className="w-8" />}
                          
                          <div className={`px-4 py-2 rounded-2xl ${
                            isOwn 
                              ? 'bg-primary-500 text-white rounded-br-md' 
                              : 'bg-gray-100 dark:bg-dark-700 text-gray-900 dark:text-white rounded-bl-md'
                          }`}>
                            {msg.content && <p className="whitespace-pre-wrap">{msg.content}</p>}
                            
                            {/* Attachment */}
                            {msg.attachment && (
                              <div className="mt-2">
                                {msg.attachment_type === 'image' ? (
                                  <img 
                                    src={msg.attachment} 
                                    alt="Attachment"
                                    className="max-w-xs rounded-lg"
                                  />
                                ) : (
                                  <a 
                                    href={msg.attachment} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="flex items-center space-x-2 text-sm underline"
                                  >
                                    <Paperclip className="w-4 h-4" />
                                    <span>Attachment</span>
                                  </a>
                                )}
                              </div>
                            )}
                            
                            <p className={`text-xs mt-1 ${isOwn ? 'text-primary-100' : 'text-gray-400'}`}>
                              {new Date(msg.timestamp || msg.created_at).toLocaleTimeString([], { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                              {isOwn && msg.is_read && (
                                <span className="ml-1">✓✓</span>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    )
                  })
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500 dark:text-gray-400">No messages yet. Start the conversation!</p>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Error Message */}
              {error && (
                <div className="px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
                  {error}
                </div>
              )}

              {/* Message Input */}
              <form onSubmit={handleSend} className="p-4 border-t border-gray-200 dark:border-dark-700">
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    className="p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg transition-colors"
                    title="Attach image"
                  >
                    <Image className="w-5 h-5 text-gray-500" />
                  </button>
                  <button
                    type="button"
                    className="p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg transition-colors"
                    title="Attach file"
                  >
                    <Paperclip className="w-5 h-5 text-gray-500" />
                  </button>
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="input flex-1"
                    disabled={sending}
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim() || sending}
                    className="btn-primary p-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-gray-100 dark:bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
                  Select a conversation
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Choose a conversation from the list to start messaging
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default MessagesPage
