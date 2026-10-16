create extension if not exists pgcrypto;
create table if not exists public.family_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now()
);
alter table public.family_profiles enable row level security;
drop policy if exists profile_select_own on public.family_profiles;
create policy profile_select_own on public.family_profiles for select to authenticated using (auth.uid() = user_id);
drop policy if exists profile_insert_own on public.family_profiles;
create policy profile_insert_own on public.family_profiles for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists profile_update_own on public.family_profiles;
create policy profile_update_own on public.family_profiles for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create table if not exists public.family_devices (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 80),
  note text not null default '' check (char_length(note) <= 160),
  linked_by_consent boolean not null default false,
  created_at timestamptz not null default now()
);
alter table public.family_devices enable row level security;
drop policy if exists devices_select_own on public.family_devices;
create policy devices_select_own on public.family_devices for select to authenticated using (auth.uid() = owner_user_id);
drop policy if exists devices_insert_own on public.family_devices;
create policy devices_insert_own on public.family_devices for insert to authenticated with check (auth.uid() = owner_user_id);
drop policy if exists devices_update_own on public.family_devices;
create policy devices_update_own on public.family_devices for update to authenticated using (auth.uid() = owner_user_id) with check (auth.uid() = owner_user_id);
drop policy if exists devices_delete_own on public.family_devices;
create policy devices_delete_own on public.family_devices for delete to authenticated using (auth.uid() = owner_user_id);
grant select, insert, update, delete on public.family_devices to authenticated;
grant select, insert, update on public.family_profiles to authenticated;
-- Nenhuma tabela de senhas de redes sociais ou mensagens privadas.
