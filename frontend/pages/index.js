import { useSession, signOut } from 'next-auth/react';
import { useState } from 'react';
import { useRouter } from 'next/router';
import ProtectedRoute from '../components/ProtectedRoute';
import LangToggle from '../components/LangToggle';
import en from '../locales/en.json';
import ar from '../locales/ar.json';

const STATUS_LABELS = {
  in_progress: 'status.in_progress',
  additional_info: 'status.additional_info',
  approved: 'status.approved',
  rejected: 'status.rejected',
  human_review: 'status.human_review',
};
const STATUS_DESC = {
  in_progress: 'dashboard.status.desc.in_progress',
  additional_info: 'dashboard.status.desc.additional_info',
  approved: 'dashboard.status.desc.approved',
  rejected: 'dashboard.status.desc.rejected',
  human_review: 'dashboard.status.desc.human_review',
};

function StatusCard({ t, status, confidence, applicationId }) {
  const pct = confidence != null ? Math.round(confidence * 100) : 0;
  const level = pct < 40 ? 'low' : pct < 70 ? 'medium' : 'high';
  return (
    <div className="card">
      <h2>{t['dashboard.status']}</h2>
      <span className={`status-badge ${status}`}>
        {t[STATUS_LABELS[status]]}
      </span>
      <p className="status-desc">{t[STATUS_DESC[status]]}</p>
      <div className="confidence-meter">
        <label>{t['dashboard.status.explanation']}</label>
        <div className="confidence-bar">
          <div className={`confidence-fill ${level}`} style={{ width: `${pct}%` }} />
        </div>
        <div className="confidence-label">{pct}%</div>
      </div>
      {applicationId && <p className="application-id">ID: {applicationId}</p>}
    </div>
  );
}

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const router = useRouter();
  const t = router.locale === 'ar' ? ar : en;
  const { data: session } = useSession();
  const [status, setStatus] = useState('in_progress');
  const [confidence, setConfidence] = useState(0);
  const [applicationId, setApplicationId] = useState(null);
  const [showForm, setShowForm] = useState(true);
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSubmitError('');
    const form = e.target;
    const remarks = form.remarks.value;
    const agreement = form.agreement.checked;
    const files = form.docs.files;
    const applicantId = session?.user?.id || session?.user?.email || '';

    if (!remarks || remarks.length < 20) {
      setSubmitError(t['form.error.minRemarks']);
      setLoading(false);
      return;
    }
    if (!agreement) {
      setSubmitError(t['form.error.agreement']);
      setLoading(false);
      return;
    }
    if (!files || files.length === 0) {
      setSubmitError(t['form.error.docs']);
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('applicant_id', applicantId);
    formData.append('remarks', remarks);
    formData.append('agreement', agreement);
    for (let i = 0; i < files.length; i++) formData.append('docs', files[i]);

    try {
      const res = await fetch(`${apiUrl}/api/submit`, { method: 'POST', body: formData });
      const data = await res.json();
      setStatus(data.status || 'in_progress');
      setConfidence(data.confidence ?? 0);
      setApplicationId(data.application_id);
      setShowForm(false);
    } catch (err) {
      setSubmitError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-main">
      <div className="dashboard-header">
        <div>
          <h1>{t['app.title']}</h1>
          <span className="dashboard-user">
            {session?.user?.name || session?.user?.email}
          </span>
        </div>
        <div className="dashboard-actions">
          <LangToggle />
          <button onClick={() => signOut()}>{t['dashboard.logout']}</button>
        </div>
      </div>

      <StatusCard t={t} status={status} confidence={confidence} applicationId={applicationId} />

      {showForm && (
        <div className="card dashboard-form">
          <h2>{t['dashboard.form.title']}</h2>
          <form onSubmit={handleSubmit}>
            <div>
              <label>
                {t['form.label.remarks']} *<br />
                <textarea
                  name="remarks"
                  minLength="20"
                  required
                />
              </label>
            </div>
            <div>
              <label>
                {t['form.label.supportingDocs']} *<br />
                <input
                  type="file"
                  name="docs"
                  multiple
                  accept=".pdf,image/png,image/jpeg"
                  required
                />
              </label>
              <div className="file-hint">PDF, JPG, PNG — max 5 files, 15MB each</div>
            </div>
            <div className="checkbox-row">
              <input type="checkbox" name="agreement" required />
              <label>{t['form.label.agreement']}</label>
            </div>
            {submitError && <p className="form-error">{submitError}</p>}
            <button className="submit-btn" type="submit" disabled={loading}>
              {loading ? 'Submitting...' : t['form.button.submit']}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}