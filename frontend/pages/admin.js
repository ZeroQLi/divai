import { useState, useEffect } from 'react';

const STATUS_LABELS = {
  in_progress: 'In Progress',
  additional_info: 'Additional Info',
  approved: 'Approved',
  rejected: 'Rejected',
  human_review: 'Human Review',
};

export default function Admin() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchDecisions = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/decisions`);
      if (res.ok) {
        setDecisions(await res.json());
      }
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
    const interval = setInterval(fetchDecisions, 30000);
    return () => clearInterval(interval);
  }, []);

  const pct = (v) => v != null ? `${Math.round(v * 100)}%` : '—';

  return (
    <div className="admin-page">
      <div className="admin-header">
        <div className="admin-header-left">
          <h1>Admin — Decisions</h1>
          <span className="admin-row-count">{decisions.length} rows</span>
        </div>
        <div className="admin-header-right">
          <a href="/" className="admin-back-link">← Dashboard</a>
        </div>
      </div>

      {loading ? (
        <p className="admin-loading">Loading...</p>
      ) : decisions.length === 0 ? (
        <p className="admin-empty">No decisions found.</p>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>App ID</th>
                <th>Applicant</th>
                <th>Loan</th>
                <th>Old EMI</th>
                <th>New EMI</th>
                <th>Ext Mo.</th>
                <th>Conf.</th>
                <th>Status</th>
                <th>Justification</th>
                <th>Explanation</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {decisions.map((d) => (
                <tr key={d.id}>
                  <td className="admin-cell-id">{d.id}</td>
                  <td className="admin-cell-num">{d.application_id ?? '—'}</td>
                  <td className="admin-cell-id">{d.applicant_id}</td>
                  <td className="admin-cell-num">{d.loan_amount != null ? (+d.loan_amount).toLocaleString() : '—'}</td>
                  <td className="admin-cell-num">{d.old_emi != null ? (+d.old_emi).toLocaleString() : '—'}</td>
                  <td className="admin-cell-num">{d.new_emi != null ? (+d.new_emi).toLocaleString() : '—'}</td>
                  <td className="admin-cell-num">{d.extended_months ?? 0}m</td>
                  <td className="admin-cell-num">
                    <span className={`admin-confidence ${(d.confidence ?? 0) < 0.4 ? 'low' : (d.confidence ?? 0) < 0.7 ? 'medium' : 'high'}`}>
                      {pct(d.confidence)}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${d.status}`}>
                      {STATUS_LABELS[d.status] || d.status}
                    </span>
                  </td>
                  <td className="admin-cell-text">{d.justification || '—'}</td>
                  <td className="admin-cell-text">{d.explanation || '—'}</td>
                  <td className="admin-cell-date">{d.created_at ? new Date(d.created_at).toLocaleString() : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
