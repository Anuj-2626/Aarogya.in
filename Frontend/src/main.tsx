import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'

import App from './App'
import { PatientProvider } from '@/contexts/PatientContext'
import { InterviewProvider } from '@/contexts/InterviewContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PatientProvider>
      <InterviewProvider>
        <App />
      </InterviewProvider>
    </PatientProvider>
  </StrictMode>,
)