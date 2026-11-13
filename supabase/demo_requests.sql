-- Demo requests from the KaiTech website. Run once in the Supabase SQL editor.
create table if not exists public.demo_requests (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text not null,
  business    text not null,
  email       text not null,
  phone       text not null default '',
  product     text not null default 'Not sure yet',
  message     text not null default '',
  handled     boolean not null default false   -- tick this in the table editor once you have replied
);

-- Row level security on, with no policies: the public keys can neither read nor write this table.
-- Only the website's server function, which uses the service role key, can insert.
alter table public.demo_requests enable row level security;
revoke all on public.demo_requests from anon, authenticated;
