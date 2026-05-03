-- ─────────────────────────────────────────────────────────────────────────────
-- ERP Management App — Supabase Database Schema
--
-- HOW TO USE:
--   1. Open your Supabase project → SQL Editor → New query
--   2. Paste this entire file and click Run
--   3. All tables and seed data will be created
-- ─────────────────────────────────────────────────────────────────────────────

-- Sites table
create table if not exists sites (
    id       serial primary key,
    name     text not null,
    short    text not null,
    location text not null,
    status   text not null default 'active'
);

-- Departments table
create table if not exists departments (
    id          serial primary key,
    name        text not null,
    description text default ''
);

-- Employees table
create table if not exists employees (
    id                text primary key,          -- EMP001, EMP002 …
    name              text not null,
    role              text not null,
    phone             text not null,
    status            text not null default 'active',
    address           text default '',
    site_id           integer references sites(id),
    department_id     integer references departments(id),
    joining_date      date not null,
    wage_per_day      integer not null,
    aadhaar           text default '',
    bank_account      text default '',
    emergency_contact text default ''
);

-- Attendance table (unique per employee per day)
create table if not exists attendance (
    id      serial primary key,
    emp_id  text references employees(id),
    date    date not null,
    status  text not null,          -- present | half_day | absent
    hours   integer default 0,
    unique(emp_id, date)
);

-- Payments table
create table if not exists payments (
    id      serial primary key,
    emp_id  text references employees(id),
    date    date not null,
    type    text not null,          -- weekly_wage | daily_wage | advance | bonus | other
    amount  integer not null,
    note    text default ''
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Seed Data
-- ─────────────────────────────────────────────────────────────────────────────

insert into sites (name, short, location, status) values
    ('Sarojini Nagar Project', 'SNP', 'Lucknow', 'active'),
    ('Gomti Nagar Extension',  'GNE', 'Lucknow', 'active')
on conflict do nothing;

insert into departments (name, description) values
    ('Civil',       'Masonry, concrete, structural work'),
    ('Electrical',  'Wiring, panels, lighting'),
    ('Plumbing',    'Pipes, drainage, fixtures'),
    ('Finishing',   'Painting, tiling, carpentry'),
    ('Supervision', 'Site engineers and supervisors')
on conflict do nothing;

insert into employees (id, name, role, phone, status, address, site_id, department_id, joining_date, wage_per_day, aadhaar, bank_account, emergency_contact) values
    ('EMP001', 'Ramesh Kumar',   'Mason',          '+91-9876543210', 'active',   'Village Rampur, Lucknow', 1, 1, '2024-01-15', 750,  '1234-5678-9012', 'SBI - 1234',  'Suresh Kumar - 9876543211'),
    ('EMP002', 'Suresh Yadav',  'Helper',          '+91-9876543220', 'active',   'Aashiyana, Lucknow',      1, 1, '2024-02-01', 500,  '2345-6789-0123', 'PNB - 2345',  'Ramesh Yadav - 9876543221'),
    ('EMP003', 'Mohan Lal',     'Electrician',     '+91-9876543230', 'active',   'Indira Nagar, Lucknow',   1, 2, '2024-01-20', 850,  '3456-7890-1234', 'BOB - 3456',  'Sohan Lal - 9876543231'),
    ('EMP004', 'Anil Singh',    'Plumber',         '+91-9876543240', 'on_leave', 'Rajajipuram, Lucknow',    1, 3, '2024-03-01', 800,  '4567-8901-2345', 'SBI - 4567',  'Sunil Singh - 9876543241'),
    ('EMP005', 'Vijay Sharma',  'Site Supervisor', '+91-9876543250', 'active',   'Gomti Nagar, Lucknow',    2, 5, '2024-01-10', 1200, '5678-9012-3456', 'HDFC - 5678', 'Ajay Sharma - 9876543251'),
    ('EMP006', 'Rakesh Gupta',  'Carpenter',       '+91-9876543260', 'active',   'Alambagh, Lucknow',       2, 4, '2024-02-15', 900,  '6789-0123-4567', 'SBI - 6789',  'Mahesh Gupta - 9876543261'),
    ('EMP007', 'Santosh Mishra','Painter',         '+91-9876543270', 'active',   'Chowk, Lucknow',          2, 4, '2024-03-10', 700,  '7890-1234-5678', 'PNB - 7890',  'Dinesh Mishra - 9876543271'),
    ('EMP008', 'Dinesh Patel',  'Site Engineer',   '+91-9876543280', 'active',   'Hazratganj, Lucknow',     2, 5, '2024-01-05', 1500, '8901-2345-6789', 'ICICI - 8901','Naresh Patel - 9876543281')
on conflict do nothing;
