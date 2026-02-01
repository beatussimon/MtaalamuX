import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'

const faqs = [
  {
    question: 'What is MtaalamuX?',
    answer: 'MtaalamuX is a platform connecting professionals with clients and peers. It allows professionals to showcase their work, articles, and services while helping users find the right experts for their needs.',
  },
  {
    question: 'How do I become a professional?',
    answer: 'To become a professional, create an account and complete your profile. You can then apply to become a verified professional through your dashboard.',
  },
  {
    question: 'Is it free to use MtaalamuX?',
    answer: 'Yes, basic usage of MtaalamuX is free. We also offer premium features for professionals who want enhanced visibility and additional tools.',
  },
  {
    question: 'How do I contact a professional?',
    answer: 'You can send a message to any professional by visiting their profile and clicking the "Message" button. You need to be logged in to send messages.',
  },
  {
    question: 'How do I post a job?',
    answer: 'Job posting is available to verified accounts. Navigate to the Jobs section and look for the "Post a Job" option in your dashboard.',
  },
  {
    question: 'How does the review system work?',
    answer: 'After working with a professional, you can leave a review and rating. This helps other users make informed decisions and helps professionals build their reputation.',
  },
]

function FAQPage() {
  const [openIndex, setOpenIndex] = useState(null)

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-3xl mx-auto">
      <div className="text-center mb-12">
        <HelpCircle className="w-16 h-16 mx-auto text-primary-600 dark:text-primary-400 mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Frequently Asked Questions</h1>
        <p className="text-gray-500 dark:text-gray-400">Find answers to common questions about MtaalamuX</p>
      </div>

      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card overflow-hidden"
          >
            <button
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
            >
              <span className="font-semibold text-gray-900 dark:text-white">{faq.question}</span>
              {openIndex === index ? (
                <ChevronUp className="w-5 h-5 text-gray-500" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-500" />
              )}
            </button>
            <AnimatePresence>
              {openIndex === index && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="border-t border-gray-100 dark:border-dark-700"
                >
                  <p className="px-6 py-4 text-gray-600 dark:text-gray-300">{faq.answer}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      <div className="mt-12 text-center">
        <p className="text-gray-500 dark:text-gray-400 mb-4">Still have questions?</p>
        <a href="/feedback" className="btn-primary">Contact Us</a>
      </div>
    </motion.div>
  )
}

export default FAQPage
