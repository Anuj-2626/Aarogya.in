import { BrowserRouter, Route, Routes } from 'react-router-dom'

import PatientLayout from '@/layouts/PatientLayout'
import DoctorLayout from '@/layouts/DoctorLayout'
import ProtectedRoute from '@/routes/ProtectedRoute'

import Landing from '@/pages/common/Landing'
import NotFound from '@/pages/common/NotFound'

import PatientRegistration from '@/pages/patient/PatientRegistration'
import Consent from '@/pages/patient/Consent'
import LanguageSelection from '@/pages/patient/LanguageSelection'
import Interview from '@/pages/patient/Interview'
import Documents from '@/pages/patient/Documents'
import Timeline from '@/pages/patient/Timeline'
import Summary from '@/pages/patient/Summary'
import PatientComplete from '@/pages/patient/PatientComplete'

import Login from '@/pages/doctor/Login'
import Dashboard from '@/pages/doctor/Dashboard'
import PatientView from '@/pages/doctor/PatientView'
import Consultation from '@/pages/doctor/Consultation'

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Landing */}
        <Route path="/" element={<Landing />} />

        {/* Patient Application */}
        <Route element={<PatientLayout />}>
          <Route
            path="/patient/register"
            element={<PatientRegistration />}
          />

          <Route
            path="/patient/consent"
            element={<Consent />}
          />

          <Route
            path="/patient/language"
            element={<LanguageSelection />}
          />

          <Route
            path="/patient/interview"
            element={<Interview />}
          />

          <Route
            path="/patient/documents"
            element={<Documents />}
          />

          <Route
            path="/patient/timeline"
            element={<Timeline />}
          />

          <Route
            path="/patient/summary"
            element={<Summary />}
          />

          <Route
            path="/patient/complete"
            element={<PatientComplete />}
          />
        </Route>

        {/* Doctor Application */}
        <Route element={<DoctorLayout />}>
          {/* Public */}
          <Route
            path="/doctor/login"
            element={<Login />}
          />

          {/* Protected */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="/doctor/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/doctor/patients/:patientId"
              element={<PatientView />}
            />

            <Route
              path="/doctor/consultation/:sessionId"
              element={<Consultation />}
            />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default AppRoutes