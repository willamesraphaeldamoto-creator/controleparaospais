# ControleParaOsPais

Projeto inicial para Chrome no PC e celular: frontend HTML/CSS/JS, autenticação Supabase e backend Python/FastAPI.

## Incluído
- Cadastro, login, logout e recuperação de senha via Supabase Auth.
- Painel responsivo e lista de dispositivos por usuário.
- FastAPI valida o token Supabase antes de responder a rotas protegidas.
- SQL inicial com Row Level Security (RLS).
- GitHub Actions para verificar sintaxe Python e publicar o frontend no GitHub Pages.

## Limites reais
Este scaffold não lê mensagens privadas, não captura senhas de Instagram/WhatsApp/Google e não monitora dispositivos escondido. Integrações externas não aparecem como conectadas sem implementação e autorização reais. A API pública do YouTube não disponibiliza livremente o histórico pessoal de visualização. Notificações push ainda não estão implementadas.

## Configurar Supabase
1. No Supabase, abra Project Settings → API.
2. Copie Project URL e chave publishable/anon.
3. Preencha `frontend/js/config.js`.
4. Execute `supabase/schema.sql` no SQL Editor.
5. Em Authentication → URL Configuration, cadastre as URLs local e de produção.
6. Não use `service_role` no frontend. A chave publishable/anon exige RLS corretamente configurado.

## Executar localmente
Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Frontend, em outro terminal:
```bash
cd frontend
python -m http.server 8080
```
Abra `http://localhost:8080`. A documentação da API fica em `http://127.0.0.1:8000/docs`.

## Publicação
O workflow `.github/workflows/pages.yml` publica automaticamente a pasta `frontend/` no GitHub Pages quando há push para `main`. Se solicitado pelo GitHub, em Settings → Pages escolha **GitHub Actions** como fonte. O endereço esperado é `https://willamesraphaeldamoto-creator.github.io/controleparaospais/`, após o workflow terminar com sucesso.

GitHub Pages hospeda apenas arquivos estáticos, não executa FastAPI. Publique `backend/` em um serviço Python com HTTPS; configure `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` e `CORS_ORIGINS` no ambiente do backend. Atualize `API_BASE_URL` em `frontend/js/config.js` com a URL real do backend. Não envie `.env` ao GitHub.

## Antes de produção
A lista de dispositivos do backend neste scaffold usa memória temporária e será perdida quando o processo reiniciar. Para persistência, conectar as rotas às tabelas Supabase com RLS ou a um banco no servidor. O SQL fornece o esquema inicial, mas o fluxo seguro de convite/vínculo de dispositivos ainda precisa ser implementado. Configure HTTPS, limites de requisição e teste RLS com contas diferentes.