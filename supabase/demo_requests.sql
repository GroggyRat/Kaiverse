-- Demo requests from the KaiTech website (kaiverse). Run once in the Supabase SQL editor.
-- The website only holds the project's public key, and that key can only add rows here:
-- it cannot read this table or touch anything else in the database.
create table if not exists public.demo_requests (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text not null check (char_length(name) between 1 and 120),
  business    text not null check (char_length(business) between 1 and 160),
  email       text not null check (char_length(email) <= 200 and email ~ '^[^\s@]+@[^\s@]+\.[^\s@]+$'),
  phone       text not null default '' check (char_length(phone) <= 40),
  product     text not null default 'Not sure yet' check (product in ('KaiWorkforce', 'BillZilla', 'KaiInspect', 'Drivo', 'Not sure yet')),
  message     text not null default '' check (char_length(message) <= 2000),
  handled     boolean not null default false   -- tick this in the table editor once you have replied
);
comment on table public.demo_requests is 'KaiTech website demo requests, written by api/demo.js in the kaiverse repo.';

alter table public.demo_requests enable row level security;
revoke all on public.demo_requests from anon, authenticated;

-- The public key may add a request, filling in only these columns, and nothing more.
grant insert (name, business, email, phone, product, message) on public.demo_requests to anon;
drop policy if exists "website adds demo requests" on public.demo_requests;
create policy "website adds demo requests" on public.demo_requests for insert to anon with check (handled = false);
