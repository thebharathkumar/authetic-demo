import React, { FormEvent, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

type CoverageType = 'auto' | 'home' | 'renters' | 'life';

type QuoteRequest = {
  age: number;
  zip_code: string;
  state: string;
  coverage_type: CoverageType;
  household_income: number;
  owns_home: boolean;
  prior_claims: number;
};

type Quote = {
  carrier_name: string;
  monthly_premium: number;
  deductible: number;
  coverage_limit: number;
  coverage_score: number;
  value_score: number;
  risk_score: number;
  rank: number;
  rationale: string;
};

type QuoteResponse = {
  profile_id: number;
  risk: { score: number; tier: string; factors: string[] };
  quotes: Quote[];
  best_quote: Quote | null;
};

const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '/api');

const starterQuote: QuoteRequest = {
  age: 34,
  zip_code: '94105',
  state: 'CA',
  coverage_type: 'auto',
  household_income: 85000,
  owns_home: false,
  prior_claims: 0,
};

function currency(value: number, options: Intl.NumberFormatOptions = {}) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0, ...options }).format(value);
}

function App() {
  const [form, setForm] = useState<QuoteRequest>(starterQuote);
  const [result, setResult] = useState<QuoteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const topQuote = useMemo(() => result?.best_quote ?? result?.quotes[0], [result]);

  async function submitQuote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/quotes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, state: form.state.toUpperCase() }),
      });

      if (!response.ok) {
        throw new Error(`Quote API returned ${response.status}`);
      }

      setResult(await response.json());
    } catch (quoteError) {
      setError(quoteError instanceof Error ? quoteError.message : 'Unable to fetch quotes.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">React + FastAPI + PostgreSQL</p>
          <h1>Insurance quote comparison with transparent risk scoring.</h1>
          <p className="hero-copy">
            Enter a lightweight applicant profile and compare mock carriers ranked by monthly price,
            deductible, coverage strength, and a Python-generated risk tier.
          </p>
        </div>
        <div className="hero-card">
          <span>Modeled risk</span>
          <strong>{result ? result.risk.tier : 'Standard'}</strong>
          <small>{result ? `${result.risk.score}/100 risk score` : 'Live after quote submission'}</small>
        </div>
      </section>

      <section className="workspace">
        <form className="quote-form" onSubmit={submitQuote}>
          <h2>Applicant details</h2>
          <label>
            Age
            <input type="number" min="18" max="100" value={form.age} onChange={(event) => setForm({ ...form, age: Number(event.target.value) })} />
          </label>
          <div className="field-grid">
            <label>
              ZIP code
              <input maxLength={5} pattern="\d{5}" value={form.zip_code} onChange={(event) => setForm({ ...form, zip_code: event.target.value })} />
            </label>
            <label>
              State
              <input maxLength={2} value={form.state} onChange={(event) => setForm({ ...form, state: event.target.value.toUpperCase() })} />
            </label>
          </div>
          <label>
            Coverage type
            <select value={form.coverage_type} onChange={(event) => setForm({ ...form, coverage_type: event.target.value as CoverageType })}>
              <option value="auto">Auto</option>
              <option value="home">Home</option>
              <option value="renters">Renters</option>
              <option value="life">Life</option>
            </select>
          </label>
          <label>
            Household income
            <input type="number" min="0" step="1000" value={form.household_income} onChange={(event) => setForm({ ...form, household_income: Number(event.target.value) })} />
          </label>
          <div className="field-grid">
            <label>
              Prior claims
              <input type="number" min="0" max="10" value={form.prior_claims} onChange={(event) => setForm({ ...form, prior_claims: Number(event.target.value) })} />
            </label>
            <label className="toggle">
              <input type="checkbox" checked={form.owns_home} onChange={(event) => setForm({ ...form, owns_home: event.target.checked })} />
              Owns home
            </label>
          </div>
          <button type="submit" disabled={loading}>{loading ? 'Comparing…' : 'Compare quotes'}</button>
          {error && <p className="error">{error}</p>}
        </form>

        <section className="results-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Ranked recommendations</p>
              <h2>{topQuote ? `${topQuote.carrier_name} leads` : 'Quotes appear here'}</h2>
            </div>
            {topQuote && <strong>{currency(topQuote.monthly_premium, { maximumFractionDigits: 2 })}/mo</strong>}
          </div>

          {result ? (
            <>
              <div className="risk-box">
                <div>
                  <span>Risk tier</span>
                  <strong>{result.risk.tier}</strong>
                </div>
                <meter min="0" max="100" value={result.risk.score} />
                <ul>
                  {result.risk.factors.slice(0, 4).map((factor) => <li key={factor}>{factor}</li>)}
                </ul>
              </div>
              <div className="quote-list">
                {result.quotes.map((quote) => (
                  <article className="quote-card" key={quote.carrier_name}>
                    <div className="rank">#{quote.rank}</div>
                    <div>
                      <h3>{quote.carrier_name}</h3>
                      <p>{quote.rationale}</p>
                    </div>
                    <div className="quote-metrics">
                      <span>{currency(quote.monthly_premium, { maximumFractionDigits: 2 })}/mo</span>
                      <span>{currency(quote.coverage_limit)} limit</span>
                      <span>{quote.coverage_score} coverage</span>
                      <span>{quote.value_score} value</span>
                    </div>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <div className="empty-state">Submit the form to see ranked mock quotes and risk-factor explanations.</div>
          )}
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
