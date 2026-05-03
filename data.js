/* ===========================================
   ERP Management App — Data Layer
   Flask + Supabase backend
   =========================================== */

const APP_NAME = 'ERP Management App';
const API_BASE = 'http://127.0.0.1:5001';

/* ─── Auth ─────────────────────────────────── */
const Auth = {
    getOrg() {
        try { return JSON.parse(localStorage.getItem('erp_org')); } catch { return null; }
    },
    register(org_name, email, password) {
        if (this.getOrg()) return { error: 'Organisation already registered. Please log in.' };
        const org = { org_name, email, password, created_at: new Date().toISOString() };
        localStorage.setItem('erp_org', JSON.stringify(org));
        return { data: org };
    },
    login(email, password) {
        const org = this.getOrg();
        if (!org) return { error: 'No organisation registered. Please register first.' };
        if (org.email !== email) return { error: 'Email address not found.' };
        if (org.password !== password) return { error: 'Incorrect password.' };
        localStorage.setItem('erp_session', JSON.stringify({ email, org_name: org.org_name }));
        return { data: { email, org_name: org.org_name } };
    },
    logout() {
        localStorage.removeItem('erp_session');
        window.location.href = 'login.html';
    },
    getSession() {
        try { return JSON.parse(localStorage.getItem('erp_session')); } catch { return null; }
    },
    requireAuth() {
        if (!this.getSession()) { window.location.href = 'login.html'; return false; }
        return true;
    },
    updateOrg(updates) {
        const org = this.getOrg();
        if (!org) return { error: 'Not registered.' };
        const updated = { ...org, ...updates };
        localStorage.setItem('erp_org', JSON.stringify(updated));
        const session = this.getSession();
        if (session && updates.org_name) {
            session.org_name = updates.org_name;
            localStorage.setItem('erp_session', JSON.stringify(session));
        }
        return { data: updated };
    }
};

/* ─── HTTP helpers ──────────────────────────── */
async function _req(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
    }
    let r;
    try {
        r = await fetch(API_BASE + path, opts);
    } catch {
        throw new Error('Cannot reach the backend. Make sure Flask is running on port 5001.');
    }
    if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.error || `Request failed (${r.status})`);
    }
    return r.json();
}

/* ─── API ───────────────────────────────────── */
const API = {

    /* Sites */
    getSites:         ()       => _req('GET',    '/sites'),
    addSite:          (d)      => _req('POST',   '/sites', d),
    updateSite:       (id, d)  => _req('PUT',    `/sites/${id}`, d),
    deleteSite:       (id)     => _req('DELETE', `/sites/${id}`),

    /* Departments */
    getDepartments:   ()       => _req('GET',    '/departments'),
    addDepartment:    (d)      => _req('POST',   '/departments', d),
    updateDepartment: (id, d)  => _req('PUT',    `/departments/${id}`, d),
    deleteDepartment: (id)     => _req('DELETE', `/departments/${id}`),

    /* Employees */
    getEmployees(filters = {}) {
        const p = new URLSearchParams();
        if (filters.site_id)       p.set('site_id',       filters.site_id);
        if (filters.department_id) p.set('department_id', filters.department_id);
        if (filters.status)        p.set('status',        filters.status);
        if (filters.search)        p.set('search',        filters.search);
        const qs = p.toString();
        return _req('GET', '/employees' + (qs ? '?' + qs : ''));
    },
    getEmployee:      (id)     => _req('GET',    `/employees/${id}`),
    addEmployee:      (d)      => _req('POST',   '/employees', d),
    updateEmployee:   (id, d)  => _req('PUT',    `/employees/${id}`, d),
    deleteEmployee:   (id)     => _req('DELETE', `/employees/${id}`),
    relocateEmployee: (id, sid, did) =>
        _req('PUT', `/employees/${id}/relocate`, { site_id: sid, department_id: did }),

    /* Attendance */
    getAttendance:       (emp_id)  => _req('GET',  `/attendance/${emp_id}`),
    saveAttendanceBatch: (records) => _req('POST', '/attendance', records),

    /* Payments */
    getPayments: (emp_id) => _req('GET',  `/payments?emp_id=${emp_id}`),
    addPayment:  (d)      => _req('POST', '/payments', d),
};

/* ─── Compute helpers (client-side) ─────────── */
function computeAttendanceStats(records) {
    return {
        present:     records.filter(a => a.status === 'present').length,
        absent:      records.filter(a => a.status === 'absent').length,
        half_day:    records.filter(a => a.status === 'half_day').length,
        total_hours: records.reduce((s, a) => s + (a.hours || 0), 0)
    };
}
function computeTotalPaid(payments) {
    return payments.reduce((s, p) => s + p.amount, 0);
}

/* ─── Utilities ─────────────────────────────── */
function getInitials(name) { return name.split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase(); }
function formatCurrency(n) { return '₹' + n.toLocaleString('en-IN'); }
function formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}
function statusBadge(status) {
    const map = {
        active:   { cls: 'badge-active',   text: 'Active'   },
        inactive: { cls: 'badge-inactive', text: 'Inactive' },
        on_leave: { cls: 'badge-onleave',  text: 'On Leave' }
    };
    const s = map[status] || map.inactive;
    return `<span class="badge ${s.cls}">${s.text}</span>`;
}
function attendanceBadge(status) {
    const map = {
        present:  { cls: 'badge-active',   text: 'Present'  },
        absent:   { cls: 'badge-inactive', text: 'Absent'   },
        half_day: { cls: 'badge-onleave',  text: 'Half Day' }
    };
    const s = map[status] || map.inactive;
    return `<span class="badge ${s.cls}">${s.text}</span>`;
}
function getQueryParam(name) { return new URLSearchParams(window.location.search).get(name); }
