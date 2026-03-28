import { useEffect, useRef, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const LOADING_STAGES = [
  "Analyzing applicant profile...",
  "Reviewing official ICA requirements...",
  "Parsing community case patterns...",
  "Separating official and anecdotal signals...",
  "Generating PR readiness assessment...",
];

const SAMPLE_PROFILE = {
  age: 30,
  nationality: "Malaysian",
  years_in_singapore: 5,
  pass_type: "Employment Pass",
  profession: "Software Engineer",
  monthly_salary: 7000,
  education: "Bachelor's Degree",
  marital_status: "Single",
  spouse_status: "",
  children_count: 0,
  family_ties_in_singapore: false,
  prior_rejections: 0,
  language_ability: "English",
  notes: "Stable employment history in Singapore",
};

const EMPTY_FORM = {
  age: 30,
  nationality: "",
  years_in_singapore: 0,
  pass_type: "",
  profession: "",
  monthly_salary: 0,
  education: "",
  marital_status: "",
  spouse_status: "",
  children_count: 0,
  family_ties_in_singapore: false,
  prior_rejections: 0,
  language_ability: "",
  notes: "",
};

const SECTION_CONFIG = [
  { key: "official_takeaways", title: "Official ICA Takeaways" },
  { key: "community_takeaways", title: "Community Pattern Signals" },
  { key: "top_strengths", title: "Top Strengths" },
  { key: "top_risks", title: "Top Risks" },
  { key: "missing_documents", title: "Missing Documents" },
  { key: "recommended_actions", title: "Recommended Actions" },
  { key: "confidence_notes", title: "Confidence Notes" },
];

function delay(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function buildPayload(formState) {
  return {
    ...formState,
    spouse_status: formState.spouse_status || null,
  };
}

function formatSignal(signal) {
  return signal.replace(/^\w/, (value) => value.toUpperCase());
}

function getBadgeClass(signal) {
  if (signal === "strong") {
    return "badge badge-strong";
  }
  if (signal === "low") {
    return "badge badge-low";
  }
  return "badge badge-moderate";
}

function Field({ label, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}

function App() {
  const [formState, setFormState] = useState(EMPTY_FORM);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [activeStage, setActiveStage] = useState(LOADING_STAGES[0]);
  const [stageIndex, setStageIndex] = useState(0);
  const stageIntervalRef = useRef(null);

  useEffect(() => {
    if (!isLoading) {
      window.clearInterval(stageIntervalRef.current);
      stageIntervalRef.current = null;
      setStageIndex(0);
      setActiveStage(LOADING_STAGES[0]);
      return undefined;
    }

    setActiveStage(LOADING_STAGES[0]);
    setStageIndex(0);

    stageIntervalRef.current = window.setInterval(() => {
      setStageIndex((current) => {
        const nextIndex = Math.min(current + 1, LOADING_STAGES.length - 1);
        setActiveStage(LOADING_STAGES[nextIndex]);
        return nextIndex;
      });
    }, 900);

    return () => {
      window.clearInterval(stageIntervalRef.current);
    };
  }, [isLoading]);

  let scoreClass = "score-card";
  if (result?.eligibility_signal === "strong") {
    scoreClass = "score-card score-card-strong";
  } else if (result?.eligibility_signal === "low") {
    scoreClass = "score-card score-card-low";
  } else if (result?.eligibility_signal === "moderate") {
    scoreClass = "score-card score-card-moderate";
  }

  function getNormalizedValue(type, value, checked) {
    if (type === "checkbox") {
      return checked;
    }

    if (type === "number") {
      return value === "" ? "" : Number(value);
    }

    return value;
  }

  function handleChange(event) {
    const { name, type, value, checked } = event.target;

    setFormState((current) => ({
      ...current,
      [name]: getNormalizedValue(type, value, checked),
    }));
  }

  function handleLoadSample() {
    setFormState(SAMPLE_PROFILE);
    setErrorMessage("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    try {
      const payload = buildPayload(formState);
      const responsePromise = fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const [response] = await Promise.all([responsePromise, delay(4500)]);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setErrorMessage(
        "We couldn’t reach the analysis service just now. Please retry when the backend is running.",
      );
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Singapore PR Readiness</p>
        <h1>Assess PR readiness with official ICA guidance and real case patterns.</h1>
        <p className="hero-copy">
          Capture the essentials, separate official rules from anecdotal
          signals, and turn a raw profile into a practical PR strategy
          snapshot.
        </p>
      </section>

      <section className="content-grid">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Applicant Profile</p>
              <h2>Profile Intake Form</h2>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={handleLoadSample}
            >
              Load Sample Profile
            </button>
          </div>

          <div className="form-grid">
            <Field label="Age">
              <input
                min="0"
                max="120"
                name="age"
                type="number"
                value={formState.age}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Nationality">
              <input
                name="nationality"
                type="text"
                value={formState.nationality}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Years in Singapore">
              <input
                min="0"
                name="years_in_singapore"
                step="0.5"
                type="number"
                value={formState.years_in_singapore}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Pass Type">
              <input
                name="pass_type"
                type="text"
                value={formState.pass_type}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Profession">
              <input
                name="profession"
                type="text"
                value={formState.profession}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Monthly Salary (SGD)">
              <input
                min="0"
                name="monthly_salary"
                type="number"
                value={formState.monthly_salary}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Education">
              <input
                name="education"
                type="text"
                value={formState.education}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Marital Status">
              <input
                name="marital_status"
                type="text"
                value={formState.marital_status}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Spouse Status">
              <input
                name="spouse_status"
                type="text"
                value={formState.spouse_status}
                onChange={handleChange}
                placeholder="Optional"
              />
            </Field>

            <Field label="Children Count">
              <input
                min="0"
                name="children_count"
                type="number"
                value={formState.children_count}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Prior Rejections">
              <input
                min="0"
                name="prior_rejections"
                type="number"
                value={formState.prior_rejections}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Language Ability">
              <input
                name="language_ability"
                type="text"
                value={formState.language_ability}
                onChange={handleChange}
                required
              />
            </Field>

            <label className="checkbox-field">
              <input
                checked={formState.family_ties_in_singapore}
                name="family_ties_in_singapore"
                type="checkbox"
                onChange={handleChange}
              />
              <span>Applicant has family ties in Singapore</span>
            </label>

            <Field label="Additional Notes">
              <textarea
                name="notes"
                rows="4"
                value={formState.notes}
                onChange={handleChange}
                placeholder="Add context that could help the assessment."
              />
            </Field>
          </div>

          <div className="form-actions">
            <button className="primary-button" disabled={isLoading} type="submit">
              {isLoading ? "Analyzing..." : "Analyze Readiness"}
            </button>
            {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}
          </div>
        </form>

        <section className="stack">
          <article className="panel loading-panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Live Analysis</p>
                <h2>Agent Progress</h2>
              </div>
            </div>

            {isLoading ? (
              <div className="loading-state">
                <div className="orbital-spinner" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                </div>
                <p className="loading-stage">{activeStage}</p>
                <div className="stage-list" aria-live="polite">
                  {LOADING_STAGES.map((stage, index) => (
                    <div
                      key={stage}
                      className={
                        index <= stageIndex ? "stage-item active" : "stage-item"
                      }
                    >
                      <span className="stage-dot" />
                      <span>{stage}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="idle-state">
                <p>Ready to analyze a profile.</p>
                <p>
                  Load the sample profile for a one-click demo, or enter a real
                  applicant scenario to assess Singapore PR readiness.
                </p>
              </div>
            )}
          </article>

          <article className="panel result-panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Assessment Output</p>
                <h2>Readiness Dashboard</h2>
              </div>
            </div>

            {result ? (
              <div className="result-content">
                <div className="hero-metrics">
                  <div className={scoreClass}>
                    <span className="score-label">Readiness Score</span>
                    <strong>{result.readiness_score}</strong>
                    <span className="score-scale">out of 100</span>
                  </div>
                  <div className="signal-card">
                    <span className="score-label">Eligibility Signal</span>
                    <span className={getBadgeClass(result.eligibility_signal)}>
                      {formatSignal(result.eligibility_signal)}
                    </span>
                    <p className="signal-copy">
                      A quick view of how prepared and competitive the PR
                      profile currently looks.
                    </p>
                  </div>
                </div>

                {result.error_note ? (
                  <div className="notice-card">
                    <p className="notice-title">Service Note</p>
                    <p>{result.error_note}</p>
                  </div>
                ) : null}

                <div className="result-grid">
                  {SECTION_CONFIG.map((section) => (
                    <div className="result-card" key={section.key}>
                      <h3>{section.title}</h3>
                      <ul>
                        {result[section.key]?.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>

                <div className="sources-card">
                  <h3>Data Sources Used</h3>
                  <p>
                    <strong>Official:</strong>{" "}
                    {result.data_sources_used?.official_source}
                  </p>
                  <p>
                    <strong>Community:</strong>{" "}
                    {result.data_sources_used?.community_source}
                  </p>
                  <p className="sources-note">
                    Official ICA guidance remains authoritative. Community
                    patterns are shown as anecdotal signals only.
                  </p>
                </div>
              </div>
            ) : (
              <div className="idle-state">
                <p>No assessment yet.</p>
                <p>
                  Submit the profile form to generate a PR readiness score,
                  evidence-aware risk summary, and recommended next steps.
                </p>
              </div>
            )}
          </article>
        </section>
      </section>
    </main>
  );
}

export default App;
