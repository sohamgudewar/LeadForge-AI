import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const EXAMPLE_COMPANIES = ["Stripe", "HubSpot", "Slack"];

const isObject = (value) => value && typeof value === "object";
const asList = (value) => (Array.isArray(value) ? value : []);
const legacyText = (value) => (typeof value === "string" ? value : "");

function Panel({ title, eyebrow, children, className = "" }) {
  return (
    <section className={`rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl shadow-black/10 sm:p-6 ${className}`}>
      {eyebrow && <p className="mb-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">{eyebrow}</p>}
      <h2 className="mb-4 text-xl font-semibold text-white">{title}</h2>
      {children}
    </section>
  );
}

function BulletList({ items }) {
  if (!items.length) return <p className="text-sm text-slate-500">No details available.</p>;
  return (
    <ul className="space-y-2 text-sm text-slate-300">
      {items.map((item, index) => (
        <li key={`${item}-${index}`} className="flex gap-2">
          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function Score({ label, value }) {
  const score = Number(value) || 0;
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{label}</span>
        <span className="font-semibold text-white">{score}/10</span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500" style={{ width: `${score * 10}%` }} />
      </div>
    </div>
  );
}

function App() {
  const [company, setCompany] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [leads, setLeads] = useState([]);

  const loadLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/leads`);
      setLeads(response.data);
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load lead history. Please check the backend.");
    } finally {
      setHistoryLoading(false);
    }
  };

  const loadLead = async (leadId) => {
    setError("");
    try {
      const response = await axios.get(`${API_URL}/lead/${leadId}`);
      setResult(response.data);
      setCompany(response.data.company || "");
    } catch (requestError) {
      console.error(requestError);
      setError(requestError.response?.data?.detail || "Could not load this lead.");
    }
  };

  const runAgent = async (event) => {
    event.preventDefault();
    if (!company.trim()) {
      setError("Enter a company name first.");
      return;
    }

    setLoading(true);
    setError("");
    setCopied(false);

    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append("company", company);
        formData.append("file", file);
        response = await axios.post(`${API_URL}/run-agent-with-pdf`, formData);
      } else {
        response = await axios.post(`${API_URL}/run-agent`, { company });
      }
      setResult(response.data);
      await loadLeads();
    } catch (requestError) {
      console.error(requestError);
      const detail = requestError.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Unable to generate outreach. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyEmail = async () => {
    const email = result?.email;
    const text = isObject(email)
      ? `Subject: ${email.subject}\n\n${email.body}\n\n${email.call_to_action}`
      : legacyText(email);
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Your browser blocked clipboard access.");
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    axios.get(`${API_URL}/leads`, { signal: controller.signal })
      .then((response) => setLeads(response.data))
      .catch((requestError) => {
        if (requestError.code !== "ERR_CANCELED") {
          console.error(requestError);
          setError("Could not load lead history. Please check the backend.");
        }
      })
      .finally(() => setHistoryLoading(false));
    return () => controller.abort();
  }, []);

  const research = isObject(result?.research) ? result.research : null;
  const enrichment = isObject(result?.enrichment) ? result.enrichment : null;
  const leadScore = isObject(result?.lead_score) ? result.lead_score : null;
  const personalization = isObject(result?.personalization) ? result.personalization : null;
  const email = isObject(result?.email) ? result.email : null;
  const review = isObject(result?.review) ? result.review : null;
  const revisions = result?.revision_count ?? review?.revision_count ?? 0;
  const researchSources = asList(research?.sources);
  const sourcesById = Object.fromEntries(
    researchSources.map((source) => [source.source_id, source])
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto grid min-h-screen max-w-[1600px] lg:grid-cols-[280px_1fr]">
        <aside className="border-b border-slate-800 bg-slate-950/90 p-5 lg:border-b-0 lg:border-r lg:p-6">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 font-black text-slate-950">LF</div>
            <div>
              <p className="font-semibold text-white">LeadForge AI</p>
              <p className="text-xs text-slate-500">Evidence-ready outreach</p>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Lead history</h2>
            <span className="rounded-full bg-slate-900 px-2 py-0.5 text-xs text-slate-500">{leads.length}</span>
          </div>

          <div className="mt-3 flex gap-2 overflow-x-auto pb-1 lg:block lg:space-y-2 lg:overflow-visible">
            {historyLoading && <p className="text-sm text-slate-500">Loading leads…</p>}
            {!historyLoading && leads.length === 0 && <p className="text-sm text-slate-500">Your generated leads will appear here.</p>}
            {leads.map((lead) => (
              <button
                type="button"
                key={lead.id}
                onClick={() => loadLead(lead.id)}
                className="min-w-44 rounded-xl border border-slate-800 bg-slate-900 px-3 py-3 text-left text-sm text-slate-300 transition hover:border-cyan-500/50 hover:text-white lg:w-full"
              >
                <span className="block truncate font-medium">{lead.company}</span>
                <span className="mt-1 block text-xs text-slate-600">Lead #{lead.id}</span>
              </button>
            ))}
          </div>
        </aside>

        <main className="min-w-0 px-4 py-8 sm:px-8 lg:px-12 lg:py-12">
          <header className="max-w-3xl">
            <p className="text-sm font-medium text-cyan-400">AI sales research workspace</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-5xl">Turn company context into reviewed outreach.</h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
              Research, qualify, personalize, and review a prospect with a bounded LangGraph workflow.
            </p>
          </header>

          <form onSubmit={runAgent} className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 sm:p-6">
            <label htmlFor="company" className="text-sm font-medium text-slate-200">Company to research</label>
            <div className="mt-2 flex flex-col gap-3 sm:flex-row">
              <input
                id="company"
                type="text"
                maxLength={120}
                placeholder="e.g. Stripe"
                value={company}
                onChange={(event) => setCompany(event.target.value)}
                disabled={loading}
                className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 disabled:opacity-60"
              />
              <button
                type="submit"
                disabled={loading}
                className="rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 px-6 py-3 font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Running workflow…" : "Generate outreach"}
              </button>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span>Try an example:</span>
              {EXAMPLE_COMPANIES.map((example) => (
                <button type="button" key={example} onClick={() => setCompany(example)} className="rounded-full border border-slate-800 px-2.5 py-1 hover:border-slate-600 hover:text-slate-300">
                  {example}
                </button>
              ))}
            </div>

            <div className="mt-5 border-t border-slate-800 pt-4">
              <label htmlFor="company-pdf" className="block text-xs font-medium uppercase tracking-wider text-slate-500">Optional company context</label>
              <input
                id="company-pdf"
                type="file"
                accept="application/pdf,.pdf"
                disabled={loading}
                onChange={(event) => setFile(event.target.files[0] || null)}
                className="mt-2 block w-full text-sm text-slate-400 file:mr-3 file:rounded-lg file:border-0 file:bg-slate-800 file:px-3 file:py-2 file:text-sm file:text-slate-200 hover:file:bg-slate-700"
              />
              <p className="mt-2 text-xs text-slate-600">PDF only, maximum 10 MB. Uploaded context is used for this company.</p>
            </div>

            {error && <p role="alert" className="mt-4 rounded-xl border border-red-900/60 bg-red-950/60 p-3 text-sm text-red-300">{error}</p>}
            {loading && (
              <div className="mt-5 rounded-xl border border-cyan-900/40 bg-cyan-950/20 p-4" aria-live="polite">
                <div className="flex items-center gap-3">
                  <span className="h-3 w-3 animate-pulse rounded-full bg-cyan-400" />
                  <p className="text-sm text-cyan-200">Researching, scoring, drafting, and reviewing. This can take about a minute.</p>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-500 sm:grid-cols-4">
                  {["Research", "Qualification", "Email", "Review"].map((stage) => <span key={stage} className="rounded-lg bg-slate-950/60 px-2 py-1.5 text-center">{stage}</span>)}
                </div>
              </div>
            )}
          </form>

          {!result && !loading && (
            <div className="mt-8 rounded-2xl border border-dashed border-slate-800 px-6 py-14 text-center">
              <p className="text-lg font-medium text-slate-300">No outreach generated yet</p>
              <p className="mt-2 text-sm text-slate-600">Enter a company or open a lead from history to inspect the workflow output.</p>
            </div>
          )}

          {result && (
            <div className="mt-8 space-y-5">
              <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Outreach package</p>
                  <h2 className="mt-1 text-2xl font-bold text-white">{result.company}</h2>
                </div>
                {review && (
                  <span className={`w-fit rounded-full border px-3 py-1 text-sm font-medium ${review.approved ? "border-emerald-800 bg-emerald-950/60 text-emerald-300" : "border-amber-800 bg-amber-950/60 text-amber-300"}`}>
                    {review.approved ? "Approved" : "Needs human review"} · {revisions} revision{revisions === 1 ? "" : "s"}
                  </span>
                )}
              </div>

              <div className="grid gap-5 xl:grid-cols-2">
                <Panel title="Company research" eyebrow={research?.industry || "Research"}>
                  {research ? (
                    <>
                      <p className="text-sm leading-6 text-slate-300">{research.summary}</p>
                      <div className="mt-5 grid gap-5 sm:grid-cols-2">
                        <div><h3 className="mb-2 text-sm font-medium text-white">Likely challenges</h3><BulletList items={asList(research.business_challenges)} /></div>
                        <div><h3 className="mb-2 text-sm font-medium text-white">Sales opportunities</h3><BulletList items={asList(research.sales_opportunities)} /></div>
                      </div>
                      <div className="mt-5 border-t border-slate-800 pt-4">
                        <div className="flex items-center justify-between gap-3">
                          <h3 className="text-sm font-medium text-white">Verified evidence</h3>
                          <span className={`rounded-full px-2.5 py-1 text-xs ${researchSources.length ? "bg-emerald-950 text-emerald-300" : "bg-slate-800 text-slate-500"}`}>
                            {researchSources.length ? `${researchSources.length} web sources` : "No web sources returned"}
                          </span>
                        </div>
                        {asList(research.evidence).length ? (
                          <ul className="mt-3 space-y-3">
                            {asList(research.evidence).map((evidence, index) => {
                              const source = sourcesById[evidence.source_id];
                              return (
                                <li key={`${evidence.source_id}-${index}`} className="rounded-xl bg-slate-950/70 p-3 text-sm text-slate-300">
                                  <p>{evidence.claim}</p>
                                  {source && (
                                    <a href={source.url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-xs font-medium text-cyan-400 hover:text-cyan-300 hover:underline">
                                      {evidence.source_id} · {source.title} ↗
                                    </a>
                                  )}
                                </li>
                              );
                            })}
                          </ul>
                        ) : (
                          <p className="mt-3 text-sm text-slate-500">
                            No externally verified claims are attached to this run. Treat inferred challenges as hypotheses.
                          </p>
                        )}
                      </div>
                    </>
                  ) : <p className="whitespace-pre-wrap text-sm text-slate-300">{legacyText(result.research)}</p>}
                </Panel>

                <Panel title="Lead qualification" eyebrow="Fit assessment">
                  {leadScore ? (
                    <div className="grid gap-5 sm:grid-cols-[120px_1fr]">
                      <div className="grid h-28 w-28 place-items-center rounded-full border-8 border-cyan-500/20 bg-cyan-950/30">
                        <div className="text-center"><span className="text-4xl font-bold text-cyan-300">{leadScore.score}</span><span className="text-slate-500">/10</span></div>
                      </div>
                      <div><h3 className="mb-2 text-sm font-medium text-white">Why this score</h3><BulletList items={asList(leadScore.reasons)} /></div>
                    </div>
                  ) : <p className="whitespace-pre-wrap text-sm text-slate-300">{legacyText(result.lead_score)}</p>}
                  {enrichment && (
                    <div className="mt-5 border-t border-slate-800 pt-4">
                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className="rounded-full bg-slate-800 px-3 py-1.5">Size: {enrichment.estimated_company_size}</span>
                        <span className="rounded-full bg-slate-800 px-3 py-1.5">Priority: {enrichment.outreach_priority}</span>
                        {asList(enrichment.decision_makers).map((person) => <span key={person} className="rounded-full bg-slate-800 px-3 py-1.5">{person}</span>)}
                      </div>
                    </div>
                  )}
                </Panel>
              </div>

              <Panel title="Personalization angle" eyebrow="Messaging strategy">
                <p className="text-base leading-7 text-slate-200">{personalization?.angle || legacyText(result.personalization)}</p>
              </Panel>

              <Panel title="Generated email" eyebrow="Ready to edit">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0 flex-1">
                    <p className="text-xs uppercase tracking-wider text-slate-500">Subject</p>
                    <p className="mt-1 font-semibold text-white">{email?.subject || "Outreach email"}</p>
                    <div className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-300">{email?.body || legacyText(result.email)}</div>
                    {email?.call_to_action && <p className="mt-4 border-l-2 border-cyan-500 pl-3 text-sm text-cyan-100">{email.call_to_action}</p>}
                  </div>
                  <button type="button" onClick={copyEmail} className="shrink-0 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-cyan-600 hover:text-white">
                    {copied ? "Copied ✓" : "Copy email"}
                  </button>
                </div>
              </Panel>

              {review && (
                <Panel title="Reviewer decision" eyebrow={review.approved ? "Approved by workflow" : "Revision limit reached"}>
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                    <Score label="Research" value={review.research_score} />
                    <Score label="Personalization" value={review.personalization_score} />
                    <Score label="Email" value={review.email_score} />
                    <Score label="Overall" value={review.overall_score} />
                  </div>
                  <div className="mt-5 grid gap-5 sm:grid-cols-2">
                    <div><h3 className="mb-2 text-sm font-medium text-emerald-300">Strengths</h3><BulletList items={asList(review.strengths)} /></div>
                    <div><h3 className="mb-2 text-sm font-medium text-amber-300">Remaining issues</h3><BulletList items={asList(review.issues)} /></div>
                  </div>
                </Panel>
              )}
            </div>
          )}

          <footer className="mt-12 border-t border-slate-900 py-6 text-xs text-slate-600">
            LeadForge AI · Built with FastAPI, Gemini, LangGraph, PostgreSQL, and React
          </footer>
        </main>
      </div>
    </div>
  );
}

export default App;
