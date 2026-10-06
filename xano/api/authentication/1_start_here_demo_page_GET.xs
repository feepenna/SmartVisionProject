// This endpoint provides a demo UI when pasted in your browser so you can interact with your Xano APIs for authentication, password reset, and chatbot conversation. It helps demonstrate how a backend interacts with a front-end to create a full app experience. This page is just a demo page that is meant to be removed later, not edited and built upon. 
query "1_start_here_demo_page" verb=GET {
  api_group = "Authentication"

  input {
  }

  stack {
    // Stores the Base URL of the API Group for dynamically mapping API endpoints in the demo UI
    var $api_base_url {
      value = $env.$api_baseurl
    }
  
    // HTML to render a demo UI to interact with authentication, password reset, and agent API endpoints
    util.template_engine {
      value = """
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Quick Start Demo</title>
        <meta name="color-scheme" content="light" />
        <style>
        :root{
          --primary:#4f46e5;
          --surface:#fff;
          --surface-alt:#f9fafb;
          --text:#111827;
          --muted:#6b7280;
          --border:#e5e7eb;
          --radius:12px;
          --radius-sm:8px;
          --radius-xs:6px;
          --shadow-sm:0 1px 2px rgba(0,0,0,.05);
          --shadow-md:0 4px 12px rgba(0,0,0,.08);
          --shadow-lg:0 12px 28px rgba(0,0,0,.14);
          --font-sans:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,"Apple Color Emoji","Segoe UI Emoji";
          --leading:1.6;
        }
        *,*:before,*:after{box-sizing:border-box}html,body{height:100%}
        body{margin:0;font-family:var(--font-sans);color:var(--text);background:var(--surface);line-height:var(--leading);-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
        a{color:var(--primary);text-decoration:none}a:hover{text-decoration:underline}
        .hidden{display:none!important}.text-center{text-align:center}.text-muted{color:var(--muted)}.text-sm{font-size:.875rem}.text-xs{font-size:.75rem}.font-bold{font-weight:700}
        .mt-0{margin-top:0}.mt-2{margin-top:.5rem}.mt-4{margin-top:1rem}.mt-6{margin-top:1.5rem}.mb-0{margin-bottom:0}.mb-2{margin-bottom:.5rem}.mb-4{margin-bottom:1rem}
        .card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-sm)}
        .btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;font-weight:600;border-radius:var(--radius-xs);padding:.65rem .9rem;border:1px solid transparent;cursor:pointer;transition:background .15s,color .15s,border-color .15s,box-shadow .15s}
        .btn:disabled{opacity:.6;cursor:not-allowed}.btn-primary{background:var(--primary);color:#fff}.btn-primary:hover{background:color-mix(in srgb,var(--primary) 90%,white)}
        .btn-secondary{background:var(--surface);color:var(--text);border-color:var(--border)}.btn-secondary:hover{background:var(--surface-alt)}.btn-link{background:transparent;color:var(--primary);padding:0;border:0}
        .field{display:grid;gap:.4rem}.label{font-size:.875rem;color:var(--muted)}
        .input{height:44px;border-radius:var(--radius-xs);border:1px solid var(--border);padding:0 12px;background:var(--surface);color:var(--text);outline:none}
        .input:focus{border-color:color-mix(in srgb,var(--primary) 65%,var(--border));box-shadow:0 0 0 3px color-mix(in srgb,var(--primary) 20%,transparent)}
        .textarea{min-height:44px;border-radius:var(--radius-xs);border:1px solid var(--border);padding:10px 12px;background:var(--surface);color:var(--text);outline:none;resize:vertical}
        .badge{display:inline-block;padding:.15rem .4rem;border-radius:999px;background:color-mix(in srgb,var(--primary) 10%, white);color:var(--primary);font-size:.7rem;font-weight:600}
        .divider{height:1px;background:var(--border);margin:16px 0}
        pre.code{margin:10px 0 0 0;background:#0f172a;color:#e2e8f0;padding:10px;border-radius:8px;overflow:auto;border:1px solid #1f2937;font-size:.75rem}
        code.inline{background:#eef2ff;border:1px solid #e0e7ff;border-radius:6px;padding:.1rem .35rem;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace}
        
        /* Auth layout */
        .auth{min-height:100vh;display:grid;grid-template-columns:1fr}
        .auth__brand{display:none;background:linear-gradient(135deg,color-mix(in srgb,var(--primary) 94%, black),var(--primary));color:#fff;padding:clamp(24px,6vw,64px)}
        .auth__brand .text-muted{color:rgba(255,255,255,.95)}
        .auth__content{background:var(--surface);display:grid;place-items:center;padding:clamp(24px,6vw,64px)}
        .auth__panel{width:100%;max-width:520px}.auth__badge{display:inline-block;font-size:.75rem;padding:.25rem .5rem;border-radius:999px;background:rgba(255,255,255,.14);color:#fff;letter-spacing:.04em}
        .api-card{margin-top:16px;background:rgba(255,255,255,.12);border-radius:var(--radius);padding:16px;backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.18)}
        .api-card h3{margin:0 0 8px 0;font-size:1rem}.api-list{display:grid;gap:10px;font-size:.9rem;opacity:.95}
        .api-item{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start}.api-dot{width:8px;height:8px;border-radius:999px;background:#fff;margin-top:6px}
        
        /* Info tip (tooltip) */
        .infotip{margin-top:10px;display:inline-flex;align-items:center;gap:10px;position:relative}
        .infotip__icon{width:22px;height:22px;border-radius:999px;display:grid;place-items:center;font-weight:800;font-size:.8rem;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.35);color:#fff}
        .infotip__trigger{border:0;background:none;color:#fff;font-weight:600;cursor:help;padding:0;text-align:left}
        .infotip__trigger:hover{text-decoration:underline}
        .infotip .tooltip{position:absolute;left:0;top:100%;margin-top:8px;background:rgba(0,0,0,.85);color:#fff;border:1px solid rgba(255,255,255,.25);border-radius:10px;padding:10px 12px;max-width:520px;width:max-content;box-shadow:var(--shadow-md);opacity:0;transform:translateY(-2px);pointer-events:none;transition:opacity .15s, transform .15s}
        .infotip:hover .tooltip,.infotip:focus-within .tooltip{opacity:1;transform:translateY(0);pointer-events:auto}
        
        /* High-contrast video link */
        .demo-video-link{
          color:#fff !important;
          text-decoration:underline;
          font-weight:700;
          display:inline-flex;
          align-items:center;
          gap:8px;
          margin-top:10px;
        }
        
        @media (min-width:960px){.auth{grid-template-columns:1fr 1fr}.auth__brand{display:block}}
        
        /* Chat layout + sidebar */
        .header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:0;left:0;right:0;z-index:100}
        .brand{display:flex;align-items:center;gap:10px;font-weight:700}.brand__logo{inline-size:28px;block-size:28px;border-radius:8px;background:var(--primary)}
        .chat{min-height:100vh;display:grid;grid-template-rows:auto 1fr;overflow:hidden}
        @supports (height: 100dvh){ .chat{min-height:100dvh} }
        .chat__body{display:grid;grid-template-columns:420px 1fr;min-height:0;column-gap:24px}
        .sidebar{background:var(--surface);border-right:2px solid color-mix(in srgb,var(--primary) 22%, var(--border));display:grid;grid-template-rows:auto 1fr}
        .sidebar__section{padding:16px}
        
        .messages{background:var(--surface);display:grid;grid-template-rows:1fr auto;min-height:0}
        .messages__scroll{padding:0 16px 16px;overflow:auto;min-height:0}
        
        /* Chat Intro */
        .chat__intro{
          background:linear-gradient(180deg, color-mix(in srgb,var(--primary) 8%, #fff), #fff 75%);
          padding:28px 16px 20px;
          margin:0 0 12px 0;
        }
        .intro__title{
          text-align:center;
          font-size:1.6rem;
          margin:0 0 14px 0;
          font-weight:800;
        }
        .intro__title::after{
          content:"";
          display:block;
          width:78px;
          height:4px;
          margin:10px auto 0;
          border-radius:4px;
          background:color-mix(in srgb,var(--primary) 72%, white);
        }
        .intro__card{
          max-width:980px;
          margin:0 auto;
          background:var(--surface);
          border:1px solid var(--border);
          border-radius:18px;
          padding:18px 20px;
          box-shadow:var(--shadow-md);
          display:grid;
          grid-template-columns:1.2fr 1fr;
          gap:22px;
        }
        .intro__desc p{margin:0 0 10px 0}
        .intro__list{list-style:none;padding:0;margin:0;display:grid;gap:12px}
        .intro__item{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:flex-start}
        .intro__arrow{line-height:1.2;font-weight:800;color:var(--primary)}
        .intro__item span{color:var(--text)}
        @media (max-width:920px){
          .intro__card{grid-template-columns:1fr;gap:14px}
        }
        
        /* Messages & composer */
        .message{max-width:68ch;margin:0 auto 10px auto;display:grid;gap:6px}
        .message__meta{font-size:.75rem;color:var(--muted)}
        .bubble{border-radius:14px;padding:12px 14px;border:1px solid var(--border);background:var(--surface);box-shadow:var(--shadow-sm)}
        .message--user .bubble{background:color-mix(in srgb,var(--primary) 7%,white);border-color:color-mix(in srgb,var(--primary) 22%,var(--border))}
        .typing{display:inline-flex;align-items:center;gap:8px;padding:10px 12px;background:var(--surface-alt);border-radius:12px;border:1px solid var(--border)}
        .dot{width:8px;height:8px;border-radius:999px;background:var(--muted);animation:pulse 1.4s ease-in-out infinite}
        .dot:nth-child(2){animation-delay:.15s}.dot:nth-child(3){animation-delay:.30s}
        @keyframes pulse{0%{transform:translateY(0);opacity:.7}50%{transform:translateY(-2px);opacity:1}100%{transform:translateY(0);opacity:.7}}
        
        /* Markdown in bubbles */
        .bubble ul, .bubble ol { margin:.25rem 0 .5rem 1.25rem; padding-left:1.25rem; }
        .bubble ol { list-style: decimal; }
        .bubble li { margin:.2rem 0; }
        .bubble p { margin:.4rem 0; }
        .bubble code { background:#eef2ff; border:1px solid #e0e7ff; border-radius:6px; padding:.05rem .3rem; }
        .bubble pre.code { margin-top:.5rem; }
        
        /* Callouts */
        .callout{border:1px dashed var(--border);padding:12px;border-radius:10px;background:var(--surface-alt)}
        .notice{
          border:1px solid var(--border);
          background:var(--surface-alt);
          border-radius:10px;
          padding:12px;
          border-left:4px solid color-mix(in srgb,var(--primary) 55%, var(--border));
        }
        
        /* Buttons: uniform size */
        .form-actions .btn { font-size: 1rem; }
        
        /* Composer */
        .composer{
          position:sticky;bottom:0;
          padding:12px 16px calc(12px + env(safe-area-inset-bottom));
          border-top:1px solid var(--border);
          background:var(--surface);
        }
        .composer-inner{
          width:100%;
          max-width:860px;
          margin:0 auto;
          display:grid;
          grid-template-columns:1fr auto;
          gap:10px;
        }
        .composer .textarea{min-height:44px;resize:none}
        .composer .btn{height:44px}
        
        /* Responsive: hide sidebar under 1000px */
        @media (max-width:1000px){
          .chat__body{grid-template-columns:1fr;column-gap:0}
          .sidebar{display:none}
        }
        </style>
        </head>
        <body>
        
        <!-- ===== LOGIN ===== -->
        <main id="view-login" class="auth hidden" data-view>
          <!-- LEFT -->
          <section class="auth__brand" aria-hidden="true">
            <div class="auth__panel">
              <span class="auth__badge">Xano Backend Demo</span>
              <h1 class="mt-4" style="font-size:clamp(28px,4.4vw,44px);line-height:1.1;margin-bottom:10px">Demo App</h1>
              <p class="text-muted" style="font-size:clamp(16px,2.6vw,20px)">A demo built on Xano with out-of-the-box authentication endpoints and an example Agent that lets you interact with a chatbot powered by Xano Docs.</p>
        
              <a class="demo-video-link" href="https://go.xano.co/4nKglrc" target="_blank" rel="noopener">🎬 Video: Learn how to use this Demo App</a>
        
              <div class="api-card">
                <h3>Demo Overview</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div><strong>Signup:</strong> Create new accounts through your Xano signup endpoint with secure password hashing.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Login:</strong> Authenticate users via POST request to your Xano login endpoint with email/password credentials.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Password Reset:</strong> Trigger email-based password recovery using your Xano reset endpoint.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Agent Chatbot:</strong> Interact with an example chatbot connected to an MCP with Xano Docs using Xano Agents.</div></div>
                </div>
              </div>
        
              <div class="api-card">
                <h3>Login – Technical Implementation</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div>Step 1: Input validation</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 2: POST to <code>/auth/login</code></div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 3: Generate Auth Token</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 4: Redirect to Agent chat</div></div>
                </div>
              </div>
        
              <div class="infotip" role="note">
                <div class="infotip__icon" aria-hidden="true">i</div>
                <button class="infotip__trigger" type="button" aria-describedby="tip-login">Remove the demo when you're ready</button>
                <div class="tooltip text-sm" id="tip-login">
                  When you're ready to remove the demo, delete the API endpoint <strong>GET /1_start_here_demo_page</strong> from your workspace.
                </div>
              </div>
            </div>
          </section>
        
          <!-- RIGHT -->
          <section class="auth__content">
            <form id="loginForm" class="auth__panel card" style="padding:24px" aria-labelledby="loginTitle" autocomplete="off">
              <div class="text-center">
                <h2 id="loginTitle" class="mt-0 mb-2" style="font-size:24px">Log in</h2>
                <p class="text-muted mb-4">Access your account</p>
              </div>
        
              <section class="callout mb-4" aria-label="API Integration">
                <div class="text-sm font-bold mb-2">API Integration</div>
                <div class="text-sm"><strong>Endpoint:</strong> <code id="login-endpoint" class="text-xs"></code></div>
                <div class="text-sm mt-2"><strong>Request Body:</strong> <code class="inline">{ email, password }</code></div>
                <div class="text-sm mt-2"><strong>Response:</strong> Authentication token</div>
                <p class="text-xs text-muted mt-2 mb-0">This form connects directly to your Xano authentication system for secure user login.</p>
              </section>
        
              <div class="field">
                <label class="label" for="login_email">Email</label>
                <input class="input" id="login_email" type="email" placeholder="you@example.com" autocomplete="off" />
              </div>
              <div class="field mt-4">
                <div style="display:flex;align-items:center;justify-content:space-between">
                  <label class="label" for="login_password">Password</label>
                  <button type="button" class="btn btn-link" id="btnTogglePassword">Show</button>
                </div>
                <input class="input" id="login_password" type="password" placeholder="••••••••" autocomplete="new-password" />
                <p class="text-xs text-muted mt-2 mb-0">Use at least 8 characters.</p>
              </div>
        
              <div class="mt-6 form-actions" style="display:grid;gap:10px">
                <button class="btn btn-primary" id="btnLogin" type="submit">Sign in</button>
                <a class="btn btn-secondary" href="#/signup" id="linkLoginToSignup" role="button">Create account</a>
                <a class="btn btn-link" href="#/reset" id="linkLoginToReset">Forgot password?</a>
              </div>
        
              <div role="status" aria-live="polite" id="loginStatus" class="text-sm text-muted mt-4" style="min-height:1em"></div>
            </form>
          </section>
        </main>
        
        <!-- ===== SIGNUP ===== -->
        <main id="view-signup" class="auth" data-view>
          <!-- LEFT -->
          <section class="auth__brand" aria-hidden="true">
            <div class="auth__panel">
              <span class="auth__badge">Xano Backend Demo</span>
              <h1 class="mt-4" style="font-size:clamp(28px,4.4vw,44px);line-height:1.1;margin-bottom:10px">Demo App</h1>
              <p class="text-muted" style="font-size:clamp(16px,2.6vw,20px)">A demo built on Xano with out-of-the-box authentication endpoints and an example Agent that lets you interact with a chatbot powered by Xano Docs.</p>
        
              <a class="demo-video-link" href="https://go.xano.co/4nKglrc" target="_blank" rel="noopener">🎬 Video: Learn how to use this Demo App</a>
        
              <div class="api-card">
                <h3>Demo Overview</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div><strong>Signup:</strong> Create new accounts through your Xano signup endpoint with secure password hashing.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Login:</strong> Authenticate users via POST request to your Xano login endpoint with email/password credentials.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Password Reset:</strong> Trigger email-based password recovery using your Xano reset endpoint.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Agent Chatbot:</strong> Interact with an example chatbot connected to an MCP with Xano Docs using Xano Agents.</div></div>
                </div>
              </div>
        
              <div class="api-card">
                <h3>Signup – Technical Implementation</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div>Step 1: Input validation</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 2: POST to <code>/auth/signup</code></div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 3: Generate Auth Token</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 4: Redirect to Agent chat</div></div>
                </div>
              </div>
        
              <div class="infotip" role="note">
                <div class="infotip__icon" aria-hidden="true">i</div>
                <button class="infotip__trigger" type="button" aria-describedby="tip-signup">Remove the demo when you're ready</button>
                <div class="tooltip text-sm" id="tip-signup">
                  When you're ready to remove the demo, delete the API endpoint <strong>GET /1_start_here_demo_page</strong> from your workspace.
                </div>
              </div>
            </div>
          </section>
        
          <!-- RIGHT -->
          <section class="auth__content">
            <form id="signupForm" class="auth__panel card" style="padding:24px" aria-labelledby="signupTitle" autocomplete="off">
              <div class="text-center">
                <h2 id="signupTitle" class="mt-0 mb-2" style="font-size:24px">Sign up</h2>
                <p class="text-muted mb-4">Create your account</p>
              </div>
        
              <section class="callout mb-4" aria-label="API Integration">
                <div class="text-sm font-bold mb-2">API Integration</div>
                <div class="text-sm"><strong>Endpoint:</strong> <code id="signup-endpoint" class="text-xs"></code></div>
                <div class="text-sm mt-2"><strong>Request Body:</strong> <code class="inline">{ name, email, password }</code></div>
                <div class="text-sm mt-2"><strong>Response:</strong> Authentication token</div>
                <p class="text-xs text-muted mt-2 mb-0">This form connects directly to your Xano signup system for secure account creation.</p>
              </section>
        
              <section class="notice mb-4" aria-label="Notice">
                <p class="text-sm mb-0">
                  <strong>Notice:</strong> This will create a new user in the
                  <code class="inline">user</code> table.
                </p>
              </section>
        
              <div class="field">
                <label class="label" for="signup_name">Name</label>
                <input class="input" id="signup_name" type="text" placeholder="Jane Doe" autocomplete="off" />
              </div>
              <div class="field mt-4">
                <label class="label" for="signup_email">Email</label>
                <input class="input" id="signup_email" type="email" placeholder="you@example.com" autocomplete="off" />
              </div>
              <div class="field mt-4">
                <label class="label" for="signup_password">Password</label>
                <input class="input" id="signup_password" type="password" placeholder="••••••••" autocomplete="new-password" />
              </div>
        
              <div class="mt-6 form-actions" style="display:grid;gap:10px">
                <button class="btn btn-primary" id="btnSignup" type="submit">Create account</button>
                <a class="btn btn-secondary" href="#/login" id="linkSignupToLogin" role="button">Already have an account? Sign in</a>
              </div>
        
              <div role="status" aria-live="polite" id="signupStatus" class="text-sm text-muted mt-4" style="min-height:1em"></div>
            </form>
          </section>
        </main>
        
        <!-- ===== RESET ===== -->
        <main id="view-reset" class="auth hidden" data-view>
          <!-- LEFT -->
          <section class="auth__brand" aria-hidden="true">
            <div class="auth__panel">
              <span class="auth__badge">Xano Backend Demo</span>
              <h1 class="mt-4" style="font-size:clamp(28px,4.4vw,44px);line-height:1.1;margin-bottom:10px">Demo App</h1>
              <p class="text-muted" style="font-size:clamp(16px,2.6vw,20px)">A demo built on Xano with out-of-the-box authentication endpoints and an example Agent that lets you interact with a chatbot powered by Xano Docs.</p>
        
              <a class="demo-video-link" href="https://go.xano.co/4nKglrc" target="_blank" rel="noopener">🎬 Video: Learn how to use this Demo App</a>
        
              <div class="api-card">
                <h3>Demo Overview</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div><strong>Signup:</strong> Create new accounts through your Xano signup endpoint with secure password hashing.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Login:</strong> Authenticate users via POST request to your Xano login endpoint with email/password credentials.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Password Reset:</strong> Trigger email-based password recovery using your Xano reset endpoint.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Agent Chatbot:</strong> Interact with an example chatbot connected to an MCP with Xano Docs using Xano Agents.</div></div>
                </div>
              </div>
        
              <div class="api-card">
                <h3>Password Reset – Technical Implementation</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div>Step 1: Email validation against Xano user database</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 2: Generate secure, time-limited reset token</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 3: Send email with reset link via your email service</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>Step 4: User clicks link → password reset form → update in Xano</div></div>
                </div>
              </div>
        
              <div class="infotip" role="note">
                <div class="infotip__icon" aria-hidden="true">i</div>
                <button class="infotip__trigger" type="button" aria-describedby="tip-reset">Remove the demo when you're ready</button>
                <div class="tooltip text-sm" id="tip-reset">
                  When you're ready to remove the demo, delete the API endpoint <strong>GET /1_start_here_demo_page</strong> from your workspace.
                </div>
              </div>
            </div>
          </section>
        
          <!-- RIGHT -->
          <section class="auth__content">
            <form id="resetForm" class="auth__panel card" style="padding:24px" aria-labelledby="resetTitle" autocomplete="off">
              <div class="text-center">
                <h2 id="resetTitle" class="mt-0 mb-2" style="font-size:24px">Request reset link</h2>
                <p class="text-muted mb-4">Enter your email</p>
              </div>
        
              <section class="callout mb-4" aria-label="API Integration">
                <div class="text-sm font-bold mb-2">API Integration</div>
                <div class="text-sm"><strong>Endpoint:</strong> <code id="reset-endpoint" class="text-xs"></code><span class="text-xs">?email=<em>you@example.com</em></span></div>
                <div class="text-sm mt-2"><strong>Query Param:</strong> <code class="inline">email</code></div>
                <div class="text-sm mt-2"><strong>Response:</strong> Message confirming a reset link (if the email exists)</div>
                <p class="text-xs text-muted mt-2 mb-0">This form targets your Xano reset endpoint; authentication is not required.</p>
              </section>
        
              <section class="notice mb-4" aria-label="Notice">
                <p class="text-sm mb-0"><strong>Notice:</strong> The Send Email function only sends to the instance owner's Email until you provide your own API key and settings. See the function in Xano for more info.</p>
              </section>
        
              <div class="field">
                <label class="label" for="reset_email">Email</label>
                <input class="input" id="reset_email" type="email" placeholder="you@example.com" autocomplete="off" />
              </div>
        
              <div class="mt-6 form-actions" style="display:grid;gap:10px">
                <button class="btn btn-primary" id="btnReset" type="submit">Send reset link</button>
                <a class="btn btn-secondary" href="#/login" id="linkResetToLogin" role="button">Back to login</a>
              </div>
        
              <div role="status" aria-live="polite" id="resetStatus" class="text-sm text-muted mt-4" style="min-height:1em"></div>
            </form>
          </section>
        </main>
        
        <!-- ===== UPDATE PASSWORD ===== -->
        <main id="view-update" class="auth hidden" data-view>
          <!-- LEFT -->
          <section class="auth__brand" aria-hidden="true">
            <div class="auth__panel">
              <span class="auth__badge">Xano Backend Demo</span>
              <h1 class="mt-4" style="font-size:clamp(28px,4.4vw,44px);line-height:1.1;margin-bottom:10px">Demo App</h1>
              <p class="text-muted" style="font-size:clamp(16px,2.6vw,20px)">A demo built on Xano with out-of-the-box authentication endpoints and an example Agent that lets you interact with a chatbot powered by Xano Docs.</p>
        
              <a class="demo-video-link" href="https://go.xano.co/4nKglrc" target="_blank" rel="noopener">🎬 Video: Learn how to use this Demo App</a>
        
              <div class="api-card">
                <h3>Demo Overview</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div><strong>Signup:</strong> Create new accounts through your Xano signup endpoint with secure password hashing.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Login:</strong> Authenticate users via POST request to your Xano login endpoint with email/password credentials.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Password Reset:</strong> Trigger email-based password recovery using your Xano reset endpoint.</div></div>
                  <div class="api-item"><span class="api-dot"></span><div><strong>Agent Chatbot:</strong> Interact with an example chatbot connected to an MCP with Xano Docs using Xano Agents.</div></div>
                </div>
              </div>
        
              <div class="api-card">
                <h3>Update Password – Technical Implementation</h3>
                <div class="api-list">
                  <div class="api-item"><span class="api-dot"></span><div>1) Read <code>magic_token</code> and <code>email</code> from URL</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>2) POST <code>/reset/magic-link-login</code> → store <code>authToken</code></div></div>
                  <div class="api-item"><span class="api-dot"></span><div>3) POST <code>/reset/update_password</code> with Bearer token</div></div>
                  <div class="api-item"><span class="api-dot"></span><div>4) On success, show confirmation & “Continue to app”</div></div>
                </div>
              </div>
        
              <div class="infotip" role="note">
                <div class="infotip__icon" aria-hidden="true">i</div>
                <button class="infotip__trigger" type="button" aria-describedby="tip-update">Remove the demo when you're ready</button>
                <div class="tooltip text-sm" id="tip-update">
                  When you're ready to remove the demo, delete the API endpoint <strong>GET /1_start_here_demo_page</strong> from your workspace.
                </div>
              </div>
            </div>
          </section>
        
          <!-- RIGHT -->
          <section class="auth__content">
            <form id="updateForm" class="auth__panel card" style="padding:24px" aria-labelledby="updateTitle" autocomplete="off">
              <div class="text-center">
                <h2 id="updateTitle" class="mt-0 mb-2" style="font-size:24px">Update password</h2>
                <p id="updateHint" class="text-muted mb-4">Checking your reset link…</p>
              </div>
        
              <section class="callout mb-4" aria-label="API Integration">
                <div class="text-sm font-bold mb-2">API Integration</div>
                <div class="text-sm"><strong>Magic-link login:</strong> <code id="magic-endpoint-sm" class="text-xs"></code> <span class="text-xs">(body: { magic_token, email? })</span></div>
                <div class="text-sm mt-1"><strong>Password update:</strong> <code id="update-endpoint-sm" class="text-xs"></code> <span class="text-xs">(body: { password, confirm_password }, Bearer auth)</span></div>
                <div id="updateEmailRow" class="text-sm mt-2 hidden"><strong>Email:</strong> <span id="updateEmail" class="text-xs"></span></div>
              </section>
        
              <div class="field">
                <label class="label" for="new_password">New password</label>
                <input class="input" id="new_password" type="password" placeholder="••••••••" />
              </div>
              <div class="field mt-4">
                <label class="label" for="confirm_password">Confirm new password</label>
                <input class="input" id="confirm_password" type="password" placeholder="••••••••" />
              </div>
        
              <div class="mt-6 form-actions" style="display:grid;gap:10px">
                <button class="btn btn-primary" id="btnUpdate" type="submit">Save new password</button>
                <a class="btn btn-secondary" href="#/login" id="linkUpdateToLogin" role="button">Back to login</a>
              </div>
        
              <div role="status" aria-live="polite" id="updateStatus" class="text-sm text-muted mt-4" style="min-height:1em"></div>
            </form>
        
            <section id="updateSuccess" class="auth__panel card hidden" style="padding:24px" aria-live="polite">
              <div class="text-center">
                <h2 class="mt-0 mb-2" style="font-size:24px">Password successfully saved</h2>
                <p class="text-muted mb-4">You can now continue to the app.</p>
                <button class="btn btn-primary" id="btnContinue">Continue to app</button>
              </div>
            </section>
          </section>
        </main>
        
        <!-- ===== CHAT ===== -->
        <main id="view-chat" class="chat hidden" data-view>
          <header class="header">
            <div class="brand"><div class="brand__logo" aria-hidden="true"></div><div>Xano Example Agent - Chat UI</div></div>
            <div style="display:flex;gap:10px">
              <button class="btn btn-secondary" id="btnNewChat" title="Start a new conversation">New Chat</button>
              <button class="btn btn-primary" id="btnLogout">Log out</button>
            </div>
          </header>
        
          <section class="chat__body">
            <!-- LEFT SIDEBAR: API details -->
            <aside class="sidebar" aria-label="API details">
              <div class="sidebar__section">
                <div class="text-sm text-muted mb-2">API</div>
                <div class="card" style="padding:14px">
                  <div class="text-sm"><strong>Method:</strong> <code class="inline">POST</code></div>
                  <div class="text-sm"><strong>Base URL:</strong> <code id="base-url" class="text-xs"></code></div>
                  <div class="text-sm"><strong>URL:</strong> <code id="chat-url" class="text-xs"></code></div>
                  <div class="divider"></div>
                  <div class="text-sm"><strong>Headers</strong></div>
                  <div class="text-xs" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                    <span>Authorization: Bearer</span>
                    <span id="tokenMasked" style="max-width:100%;overflow:hidden;text-overflow:ellipsis"></span>
                    <button class="btn btn-link text-xs" id="btnShowToken" type="button">Show</button>
                    <button class="btn btn-link text-xs" id="btnCopyToken" type="button">Copy</button>
                  </div>
                  <div class="text-xs">Content-Type: application/json</div>
                  <div class="divider"></div>
                  <div class="text-sm"><strong>Parameters</strong></div>
                  <ul class="text-xs" style="margin:8px 0 0 16px;line-height:1.5">
                    <li><code class="inline">message</code> — <em>array</em> of objects</li>
                    <li><code class="inline">conversation_id</code> — <em>integer</em> (optional)</li>
                  </ul>
                  <div class="divider"></div>
                  <div class="text-sm"><strong>Sample message JSON</strong></div>
                  <pre id="chat-sample" class="code"></pre>
                  <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:8px">
                    <button class="btn btn-secondary text-xs" id="btnCopyJson" type="button">Copy</button>
                  </div>
                </div>
              </div>
            </aside>
        
            <!-- RIGHT: chat UI -->
            <section class="messages" aria-live="polite">
              <div class="messages__scroll" id="scrollWrap">
                <!-- Intro block -->
                <section class="chat__intro" id="chatIntro" aria-label="Xano Example Agent Chatbot intro">
                  <h2 class="intro__title">Xano Example Agent Chatbot</h2>
                  <div class="intro__card">
                    <div class="intro__desc">
                      <p>Now that you’ve signed in using Xano’s authentication endpoints, welcome to the demo UI for interacting with the Xano Example Agent inside your instance.</p>
                      <p>As an example, this Agent includes tools connected to an MCP Server of Xano documentation — allowing it to answer your questions about Xano directly from the docs.</p>
                    </div>
                    <div>
                      <div class="text-sm text-muted" style="margin-bottom:8px">How to Explore</div>
                      <ul class="intro__list">
                        <li class="intro__item"><span class="intro__arrow" aria-hidden="true">→</span><span>To use the Agent in your own workspace, navigate to <strong>AI &gt; Agents</strong> in Xano.</span></li>
                        <li class="intro__item"><span class="intro__arrow" aria-hidden="true">→</span><span>To view the connected tools (e.g., <strong>search_xano_docs</strong>), open the <strong>Xano Example Agent</strong> in your workspace.</span></li>
                        <li class="intro__item"><span class="intro__arrow" aria-hidden="true">→</span><span>Type a message below and start interacting with the Agent chatbot.</span></li>
                      </ul>
                    </div>
                  </div>
                </section>
        
                <!-- Messages appear here -->
                <div id="messageList"></div>
              </div>
        
              <!-- Sticky composer -->
              <form id="composer" class="composer">
                <div class="composer-inner">
                  <textarea id="inputMessage" class="textarea" placeholder="Type your message…" rows="1" required></textarea>
                  <button type="submit" class="btn btn-primary" id="btnSend">Send</button>
                </div>
              </form>
            </section>
          </section>
        </main>
        
        <script>
        (() => {
          // ========= Config (dynamic from Xano) =========
          const Config = {
            baseUrl: "{{ $var.api_base_url }}", // injected by Xano
            routes: {
              login: "/auth/login",
              signup: "/auth/signup",
              me: "/auth/me",
              requestResetLink: "/reset/request-reset-link",
              magicLogin: "/reset/magic-link-login",
              updatePassword: "/reset/update_password",
              conversation: "/demo-agent/conversation"
            },
            auth: { headerName: "Authorization", scheme: "Bearer " }
          };
        
          // Normalize + optional URL override
          function normalizeBaseUrl(u){ return (u || "").trim().replace(/\/+$/,""); }
          Config.baseUrl = normalizeBaseUrl(Config.baseUrl);
          try{
            const qs = (location.search||"").slice(1);
            const hs = (location.hash||"");
            const hq = hs.includes("?") ? hs.slice(hs.indexOf("?")+1).replace(/\?/g,"&") : "";
            const get = k => new URLSearchParams(qs).get(k) || new URLSearchParams(hq).get(k);
            const override = get("api_base_url") || get("api");
            const stored = localStorage.getItem("apiBaseUrlOverride");
            if (override){ Config.baseUrl = normalizeBaseUrl(override); localStorage.setItem("apiBaseUrlOverride", Config.baseUrl); }
            else if (stored){ Config.baseUrl = normalizeBaseUrl(stored); }
          }catch{}
          console.debug("[Demo] Xano Base URL →", Config.baseUrl);
        
          // ========= App state =========
          const state = {
            token: load("authToken"),
            user: parseJSON(localStorage.getItem("user")),
            conversationId: null,
            messages: []
          };
        
          const views = {
            login:  document.getElementById("view-login"),
            signup: document.getElementById("view-signup"),
            reset:  document.getElementById("view-reset"),
            update: document.getElementById("view-update"),
            chat:   document.getElementById("view-chat")
          };
          const $ = (id) => document.getElementById(id);
        
          // ---------- Utilities ----------
          function parseJSON(s){ try{ return JSON.parse(s) }catch{ return null } }
          function save(k,v){ if (v==null || v==="") localStorage.removeItem(k); else localStorage.setItem(k,v); }
          function load(k){ return localStorage.getItem(k) }
          function show(id){ for (const k of Object.keys(views)) views[k].classList.toggle("hidden", k!==id); }
          function navigateTo(hash){ if (location.hash===hash) router(); else location.hash=hash; }
          function fullUrl(path){ return Config.baseUrl.replace(/\/+$/,"") + (path.startsWith("/")?path:"/"+path); }
          function resolveUrl(path){ return /^https?:\/\//.test(path) ? path : fullUrl(path); }
        
          // ---------- Instance key (baseUrl-aware) ----------
          function djb2_xor(str){
            let h = 5381 >>> 0;
            for (let i=0;i<str.length;i++){ h = (((h << 5) + h) ^ str.charCodeAt(i)) >>> 0; }
            return h >>> 0;
          }
          function instanceKey(){
            const b = (Config.baseUrl || "").trim().toLowerCase();
            return (djb2_xor(b)).toString(36); // compact, stable per baseUrl
          }
        
          // ---------- Per-user + per-instance scoped storage ----------
          function scopePrefix(){
            const uid = state.user?.id;
            if (uid == null) return null;
            return `i:${instanceKey()}:u:${uid}:`;
          }
          function scopedGet(key){ const p = scopePrefix(); if (!p) return null; return localStorage.getItem(p + key); }
          function scopedSet(key,val){ const p=scopePrefix(); if (!p) return; if (val==null||val==="") localStorage.removeItem(p+key); else localStorage.setItem(p+key,String(val)); }
          function scopedRemove(key){ const p = scopePrefix(); if (!p) return; localStorage.removeItem(p + key); }
          function historyKey(cid){ const p = scopePrefix(); if (!p || cid == null) return null; return `${p}conv:${cid}`; }
          function loadHistory(cid){ const k = historyKey(cid); if (!k) return []; const raw = localStorage.getItem(k); return raw ? (parseJSON(raw) || []) : []; }
          function saveHistory(cid,messages){ const k = historyKey(cid); if (!k) return; localStorage.setItem(k, JSON.stringify(messages)); }
        
          // Clean up very old, legacy keys (pre-instance scoping)
          function migrateLegacyStorage(){
            try{
              localStorage.removeItem("conversationId");
              const del=[]; for(let i=0;i<localStorage.length;i++){ const k=localStorage.key(i); if (k==="conversationId"||k?.startsWith("conv:")) del.push(k); }
              del.forEach(k=>localStorage.removeItem(k));
            }catch{}
          }
          function hydrateConversationFromScope(){
            state.messages=[]; state.conversationId=null;
            const cid=scopedGet("lastConversationId");
            if (cid){ state.conversationId=cid; state.messages=loadHistory(cid); }
            renderMessages(); updateChatSidebar();
          }
        
          // ---------- Form reset helpers ----------
          function resetForm(id){ const f=$(id); if (f && typeof f.reset==="function") f.reset(); }
          function clearAuthForms(){
            ["loginForm","signupForm","resetForm","updateForm"].forEach(resetForm);
            const ids = [
              "login_email","login_password",
              "signup_name","signup_email","signup_password",
              "reset_email",
              "new_password","confirm_password"
            ];
            ids.forEach(id => { const el=$(id); if(el){ el.value=""; } });
            const lpw = $("login_password"); if (lpw) lpw.type = "password";
            const toggle = $("btnTogglePassword"); if (toggle) toggle.textContent = "Show";
            const im = $("inputMessage"); if (im) im.value="";
          }
        
          // Merge params from search and hash
          function getAllParams(){
            const out = {};
            const add = (raw) => {
              if (!raw) return;
              const sp = new URLSearchParams(raw);
              for (const [k, v] of sp.entries()) if (!(k in out)) out[k] = v;
            };
            add((location.search || "").replace(/^\?/, ""));
            const hash = location.hash || "";
            let q = ""; const idx = hash.indexOf("?");
            if (idx >= 0) q = hash.slice(idx + 1);
            if (q) { q = q.replace(/\?/g, "&"); add(q); }
            return out;
          }
        
          // Scrub sensitive params
          function scrubSensitiveParams(keys){
            try{
              const u = new URL(window.location.href);
              keys.forEach(k => u.searchParams.delete(k));
              let hash = u.hash || "";
              if (hash.includes("?")){
                const [route, rawQ] = [hash.slice(0, hash.indexOf("?")), hash.slice(hash.indexOf("?") + 1)];
                const hsp = new URLSearchParams(rawQ.replace(/\?/g,"&"));
                keys.forEach(k => hsp.delete(k));
                const newQ = hsp.toString();
                u.hash = route + (newQ ? "?" + newQ : "");
              }
              history.replaceState(null, "", u.toString());
            }catch{}
          }
        
          // Prefer update-password if magic token present
          function autoRouteIfMagicToken(){
            const p = getAllParams();
            const hasMagic = !!(p.magic_token || p.token || p.magicToken);
            if (hasMagic && !location.hash.replace(/^#/, "").startsWith("/update-password") && !location.hash.replace(/^#/, "").startsWith("update-password")) {
              navigateTo("#/update-password");
            }
          }
        
          async function http(path,{ method="GET", body, auth=false }={}){
            const url = resolveUrl(path);
            const headers = { "Accept":"application/json" };
            if (body!=null) headers["Content-Type"]="application/json";
            if (auth && state.token) headers[Config.auth.headerName] = Config.auth.scheme + state.token;
            const res = await fetch(url, { method, headers, ...(body!=null?{body:JSON.stringify(body)}:{}), credentials:"include" });
            const text = await res.text();
            let json = null; if (text) { try{ json = JSON.parse(text) }catch{} }
            if (!res.ok) throw new Error(json?.message || json?.error || `HTTP ${res.status}`);
            return json;
          }
        
          // ---------- Clear form statuses ----------
          function clearAllFormStatuses(){
            const ids = ["loginStatus","signupStatus","resetStatus","updateStatus"];
            ids.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = ""; });
          }
        
          // ---------- Route helpers ----------
          function currentRoute(){
            const raw = (location.hash || "#/signup").slice(1);
            const noLead = raw.replace(/^\/+/, "");
            const pathOnly = noLead.split("?")[0];
            return pathOnly || "signup";
          }
        
          // ---------- Router ----------
          async function router(){
            const route = currentRoute();
            clearAllFormStatuses();
        
            switch (route) {
              case "signup":
                show("signup"); clearAuthForms(); break;
              case "login":
                show("login"); clearAuthForms(); break;
              case "reset":
                show("reset"); clearAuthForms(); break;
              case "update-password":
                show("update"); clearAuthForms();
                if (!updateBootstrapped) initUpdateOnce();
                await prepareUpdatePage();
                break;
              case "chat":
                if (!(await ensureAuthed())) { navigateTo("#/signup"); return; }
                show("chat");
                if (!chatBootstrapped) initChatOnce();
                hydrateConversationFromScope();
                break;
              default:
                navigateTo("#/signup"); return;
            }
            dumpConfig();
          }
          window.addEventListener("hashchange", router);
        
          // ---------- Auth helpers ----------
          function setSession({ token, user }){
            if (token){ state.token = token; save("authToken", token); }
            if (user){ state.user = user; localStorage.setItem("user", JSON.stringify(user)); }
            updateChatSidebar();
          }
          function clearSession(){
            state.token = null; state.user = null;
            localStorage.removeItem("authToken"); localStorage.removeItem("user");
            state.conversationId = null; state.messages = [];
            clearAllFormStatuses();
            clearAuthForms();
            updateChatSidebar();
          }
          async function ensureAuthed(){
            if (!state.token) return false;
            try{ const me = await http(Config.routes.me,{method:"GET",auth:true}); setSession({ token: state.token, user: me }); return true; }
            catch{ clearSession(); return false; }
          }
        
          // ---------- API wrappers ----------
          const api = {
            async login(email, password){
              const json = await http(Config.routes.login, { method:"POST", body:{ email, password } });
              const accessToken = json?.authToken;
              if (!accessToken) throw new Error("No authToken returned.");
              return { accessToken };
            },
            async signup(name, email, password){
              const json = await http(Config.routes.signup, { method:"POST", body:{ name, email, password } });
              const accessToken = json?.authToken;
              if (!accessToken) throw new Error("No authToken returned.");
              return { accessToken };
            },
            async requestResetLink(email){
              const url = Config.routes.requestResetLink + "?email=" + encodeURIComponent(email);
              return await http(url, { method:"GET" });
            },
            async magicLogin(magic_token, email){
              const body = { magic_token };
              if (email) body.email = email;
              const json = await http(Config.routes.magicLogin, { method:"POST", body });
              const accessToken = json?.authToken;
              if (!accessToken) throw new Error("Magic login failed (no authToken).");
              return { accessToken };
            },
            async updatePassword(password, confirm_password){
              return await http(Config.routes.updatePassword, { method:"POST", body:{ password, confirm_password }, auth:true });
            },
            async converse(text){
              const body = {
                message: [
                  { role: "user", content: [ { type: "text", text } ] }
                ]
              };
              if (state.conversationId != null && String(state.conversationId).trim() !== "") {
                const n = Number(state.conversationId);
                if (!Number.isNaN(n)) body.conversation_id = n;
              }
              const json = await http(Config.routes.conversation, { method:"POST", body, auth:true });
              return { reply: json?.result ?? "", conversationId: json?.conversation_id ?? null };
            }
          };
        
          // ---------- Markdown renderer ----------
          function renderMarkdownSafe(md){
            if (!md) return "";
            let s = String(md);
            s = s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
            const FENCES = [];
            s = s.replace(/```([\s\S]*?)```/g, (_, code) => { FENCES.push(code); return `\uE000CODE${FENCES.length-1}\uE000`; });
            s = s.replace(/`([^`]+?)`/g, "<code>$1</code>");
            s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
            s = s.replace(/(^|[^*])\*([^*\n][^*]*?)\*(?!\*)/g, "$1<em>$2</em>");
            const lines = s.split(/\r?\n/); const out=[]; let i=0;
            while(i<lines.length){
              if(/^\s*\d+\.\s+/.test(lines[i])){ const items=[]; while(i<lines.length&&/^\s*\d+\.\s+/.test(lines[i])){ items.push(lines[i].replace(/^\s*\d+\.\s+/,"").trimEnd()); i++; } out.push("<ol>"+items.map(it=>`<li>${it}</li>`).join("")+"</ol>"); continue; }
              if(/^\s*[-*]\s+/.test(lines[i])){ const items=[]; while(i<lines.length&&/^\s*[-*]\s+/.test(lines[i])){ items.push(lines[i].replace(/^\s*[-*]\s+/,"").trimEnd()); i++; } out.push("<ul>"+items.map(it=>`<li>${it}</li>`).join("")+"</ul>"); continue; }
              out.push(lines[i]); i++;
            }
            s = out.join("\n");
            s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, `<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>`);
            s = s.split(/\n{2,}/).map(chunk=>{ const t=chunk.trim(); if(!t)return""; if(/^<(ul|ol|pre|h\d|blockquote)\b/i.test(t))return t; return `<p>${t.replace(/\n/g,"<br>")}</p>`; }).join("");
            s = s.replace(/\uE000CODE(\d+)\uE000/g,(_,i)=>{ const code=String(FENCES[Number(i)]||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); return `<pre class="code"><code>${code}</code></pre>`; });
            return s;
          }
        
          // ---------- UI wiring ----------
          document.addEventListener("DOMContentLoaded", async () => {
            migrateLegacyStorage();
            autoRouteIfMagicToken();
            if (!location.hash) navigateTo("#/signup");
        
            $("linkSignupToLogin")?.addEventListener("click", (e)=>{ e.preventDefault(); clearAllFormStatuses(); clearAuthForms(); navigateTo("#/login"); });
            $("linkLoginToSignup")?.addEventListener("click", (e)=>{ e.preventDefault(); clearAllFormStatuses(); clearAuthForms(); navigateTo("#/signup"); });
            $("linkLoginToReset")?.addEventListener("click",  (e)=>{ e.preventDefault(); clearAllFormStatuses(); clearAuthForms(); navigateTo("#/reset"); });
            $("linkResetToLogin")?.addEventListener("click",  (e)=>{ e.preventDefault(); clearAllFormStatuses(); clearAuthForms(); navigateTo("#/login"); });
            $("linkUpdateToLogin")?.addEventListener("click", (e)=>{ e.preventDefault(); clearAllFormStatuses(); clearAuthForms(); navigateTo("#/login"); });
        
            // Login
            const btnTogglePassword = $("btnTogglePassword"), pw = $("login_password");
            btnTogglePassword?.addEventListener("click", () => { pw.type = pw.type==="password" ? "text" : "password"; });
        
            $("loginForm")?.addEventListener("submit", async (e) => {
              e.preventDefault();
              const email = $("login_email").value.trim();
              const password = $("login_password").value;
              $("loginStatus").textContent = "Signing in…"; $("btnLogin").disabled = true;
              try {
                const { accessToken } = await api.login(email, password);
                setSession({ token: accessToken });
                const me = await http(Config.routes.me, { method:"GET", auth:true });
                setSession({ token: accessToken, user: me });
                $("loginStatus").textContent = "Signed in.";
                navigateTo("#/chat");
              } catch (err) {
                $("loginStatus").textContent = "Sign-in failed: " + (err.message || "Unknown error");
              } finally {
                $("btnLogin").disabled = false;
              }
            });
        
            // Signup
            $("signupForm")?.addEventListener("submit", async (e) => {
              e.preventDefault();
              const name = $("signup_name").value.trim();
              const email = $("signup_email").value.trim();
              const password = $("signup_password").value;
              $("signupStatus").textContent = "Creating your account…"; $("btnSignup").disabled = true;
              try {
                const { accessToken } = await api.signup(name, email, password);
                setSession({ token: accessToken });
                const me = await http(Config.routes.me, { method:"GET", auth:true });
                setSession({ token: accessToken, user: me });
                $("signupStatus").textContent = "Account created."; navigateTo("#/chat");
              } catch (err) {
                $("signupStatus").textContent = "Signup failed: " + (err.message || "Unknown error");
              } finally {
                $("btnSignup").disabled = false;
              }
            });
        
            // Reset link
            $("resetForm")?.addEventListener("submit", async (e) => {
              e.preventDefault();
              const email = $("reset_email").value.trim();
              $("resetStatus").textContent = "Requesting link…"; $("btnReset").disabled = true;
              try {
                await api.requestResetLink(email);
                $("resetStatus").textContent = "If that email exists, a link has been sent.";
              } catch (err) {
                $("resetStatus").textContent = "Request failed: " + (err.message || "Unknown error");
              } finally {
                $("btnReset").disabled = false;
              }
            });
        
            // Update password
            $("updateForm")?.addEventListener("submit", onUpdateSubmit);
        
            // Header actions
            $("btnLogout")?.addEventListener("click", () => { clearSession(); navigateTo("#/signup"); });
            $("btnNewChat")?.addEventListener("click", newChat);
            $("btnCopyJson")?.addEventListener("click", async () => { try { const jsonText = JSON.stringify(buildSampleBody(), null, 2); await navigator.clipboard.writeText(jsonText); $("btnCopyJson").textContent = "Copied!"; setTimeout(()=>{$("btnCopyJson").textContent="Copy"}, 900);} catch {} });
            $("btnContinue")?.addEventListener("click", () => navigateTo("#/chat"));
        
            // Token show/copy
            $("btnShowToken")?.addEventListener("click", () => { tokenVisible = !tokenVisible; $("btnShowToken").textContent = tokenVisible ? "Hide" : "Show"; updateChatSidebar(); });
            $("btnCopyToken")?.addEventListener("click", async () => { try { await navigator.clipboard.writeText(state.token || ""); $("btnCopyToken").textContent = "Copied!"; setTimeout(()=>{$("btnCopyToken").textContent="Copy"}, 900);} catch {} });
        
            await router();
          });
        
          // ---------- Update Password ----------
          let updateBootstrapped = false;
          function initUpdateOnce(){ if (updateBootstrapped) return; updateBootstrapped = true; }
          function setUpdateFormEnabled(enabled){ ["new_password","confirm_password","btnUpdate"].forEach(id=>{ const el=$(id); if (el) el.disabled = !enabled; }); }
        
          async function prepareUpdatePage(){
            const set = (id,val)=>{ const el=$(id); if (el) el.textContent = val; };
            set("magic-endpoint-sm", fullUrl(Config.routes.magicLogin));
            set("update-endpoint-sm", fullUrl(Config.routes.updatePassword));
        
            const params = getAllParams();
            const magicToken = params.magic_token || params.token || params.magicToken || "";
            const email = params.email || params.e || "";
            if (email){ $("updateEmailRow")?.classList.remove("hidden"); $("updateEmail").textContent = email; }
        
            if (magicToken){
              $("updateHint").textContent = "Authenticating via magic link…";
              setUpdateFormEnabled(false);
              try{
                const { accessToken } = await api.magicLogin(magicToken, email);
                setSession({ token: accessToken });
                try { const me = await http(Config.routes.me, { method:"GET", auth:true }); setSession({ user: me }); } catch {}
                scrubSensitiveParams(["magic_token","token","magicToken"]);
                $("updateHint").textContent = "Authenticated. Enter your new password below.";
                setUpdateFormEnabled(true);
              }catch(err){
                $("updateHint").textContent = "Magic link authentication failed: " + (err.message || "Unknown error");
                setUpdateFormEnabled(false);
                return;
              }
              return;
            }
        
            if (state.token){
              $("updateHint").textContent = "Enter your new password below.";
              setUpdateFormEnabled(true);
            } else {
              $("updateHint").textContent = "Missing auth token. Open this page from your emailed reset link.";
              setUpdateFormEnabled(false);
            }
          }
        
          async function onUpdateSubmit(e){
            e.preventDefault();
            const p1 = $("new_password")?.value || "";
            const p2 = $("confirm_password")?.value || "";
            const status = $("updateStatus");
            const btn = $("btnUpdate");
        
            if (p1 !== p2){ status.textContent = "Passwords do not match."; return; }
            if (!state.token){ status.textContent = "Missing auth token. Open this page from your emailed reset link."; return; }
        
            status.textContent = "Saving…"; btn.disabled = true;
            try{
              await api.updatePassword(p1, p2);
              $("updateForm")?.classList.add("hidden");
              $("updateSuccess")?.classList.remove("hidden");
              status.textContent = "";
            }catch(err){
              status.textContent = "Update failed: " + (err.message || "Unknown error");
            }finally{
              btn.disabled = false;
            }
          }
        
          // ---------- Chat logic ----------
          let chatBootstrapped = false;
          function initChatOnce(){ if (chatBootstrapped) return; chatBootstrapped = true; $("composer")?.addEventListener("submit", sendMessageFlow); }
        
          function newChat(){
            scopedRemove("lastConversationId");
            state.conversationId=null; state.messages=[];
            renderMessages(); updateChatSidebar(); $("inputMessage")?.focus();
          }
        
          function formatTime(ts){ return new Date(ts || Date.now()).toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}); }
          function scrollContainer(){ return document.getElementById("scrollWrap"); }
        
          function renderMessages(){
            const list = $("messageList"); if (!list) return;
            const wrap = scrollContainer();
            list.innerHTML = "";
            state.messages.forEach(m => {
              const isUser = (m.role||"").toLowerCase()==="user";
              const role = isUser ? "You" : "Bot";
              const el = document.createElement("article");
              el.className = "message " + (isUser ? "message--user" : "message--assistant");
              el.innerHTML = `
                <div class="message__meta">${role} • ${formatTime(m.ts)}</div>
                <div class="bubble"></div>`;
              el.querySelector(".bubble").innerHTML = renderMarkdownSafe(m.content);
              list.appendChild(el);
            });
            if (wrap) wrap.scrollTop = wrap.scrollHeight;
          }
        
          function showTyping(){
            const wrap = scrollContainer(); if (!wrap) return;
            const typing = document.createElement("div");
            typing.id="typing"; typing.style.maxWidth="68ch"; typing.style.margin="0 auto 10px";
            typing.innerHTML = `<div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div><span class="text-sm text-muted" style="margin-left:8px">AI is typing…</span></div>`;
            wrap.appendChild(typing);
            wrap.scrollTop = wrap.scrollHeight;
          }
          function hideTyping(){ const t = $("typing"); if (t) t.remove(); }
        
          async function sendMessageFlow(e){
            e.preventDefault();
            const text = $("inputMessage").value.trim();
            if (!text) return;
            $("inputMessage").value = "";
            state.messages.push({ role:"user", content:text, ts: Date.now() });
            renderMessages(); showTyping();
            try{
              const { reply, conversationId } = await api.converse(text);
              const cidStr = conversationId != null ? String(conversationId) : null;
              if (cidStr && cidStr.trim() !== "") {
                const cidChanged = cidStr !== String(state.conversationId || "");
                state.conversationId = cidStr;
                scopedSet("lastConversationId", state.conversationId);
                if (cidChanged) {
                  const existing = loadHistory(state.conversationId);
                  if (existing.length) state.messages = existing.concat(state.messages);
                }
              }
              state.messages.push({ role:"assistant", content: reply || "", ts: Date.now() });
              if (state.conversationId) saveHistory(state.conversationId, state.messages);
              renderMessages(); updateChatSidebar();
            }catch(err){
              state.messages.push({ role:"assistant", content: "Error: " + (err.message || "Unknown error"), ts: Date.now() });
              renderMessages();
            }finally{ hideTyping(); }
          }
        
          // ---------- Sidebar helpers ----------
          function buildSampleBody(){
            const body = {
              message: [
                { role: "user", content: [ { type: "text", text: "Hello!" } ] }
              ]
            };
            const cidRaw = state.conversationId;
            if (cidRaw != null && String(cidRaw).trim() !== "") {
              const n = Number(cidRaw);
              if (!Number.isNaN(n)) body.conversation_id = n;
            }
            return body;
          }
        
          let tokenVisible = false;
          function maskToken(tok){ if (!tok) return "—"; return tok.length <= 12 ? tok : (tok.slice(0,4) + "…" + tok.slice(-4)); }
          function updateChatSidebar(){
            const endpoint = fullUrl(Config.routes.conversation);
            const urlEl = $("chat-url"); if (urlEl) urlEl.textContent = endpoint;
            const baseEl = $("base-url"); if (baseEl) baseEl.textContent = Config.baseUrl || "—";
            const tokenEl = $("tokenMasked"); if (tokenEl) tokenEl.textContent = tokenVisible ? (state.token || "—") : maskToken(state.token || "");
            const sampleEl = $("chat-sample"); if (sampleEl) sampleEl.textContent = JSON.stringify(buildSampleBody(), null, 2);
          }
        
          function dumpConfig(){
            const set = (id, val) => { const el=$(id); if (el) el.textContent = val; };
            set("login-endpoint", fullUrl(Config.routes.login));
            set("signup-endpoint", fullUrl(Config.routes.signup));
            set("reset-endpoint", fullUrl(Config.routes.requestResetLink));
            set("magic-endpoint-sm", fullUrl(Config.routes.magicLogin));
            set("update-endpoint-sm", fullUrl(Config.routes.updatePassword));
            updateChatSidebar();
          }
        
          document.addEventListener("DOMContentLoaded", dumpConfig);
        })();
        </script>
        </body>
        </html>
        """
    } as $html
  
    // Sets content-type header to text/html
    util.set_header {
      value = "Content-type: Text/HTML"
      duplicates = "replace"
    }
  }

  response = $html
  tags = ["xano:quick-start"]
  guid = "-h8cq5Hd9_ptuoJnUkyBSpc8btg"
}