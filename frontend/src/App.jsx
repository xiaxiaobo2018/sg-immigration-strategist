import { useRef, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const DASHBOARD_PREVIEW = [
  "Readiness Score",
  "Eligibility Signal",
  "Top Strengths",
  "Top Risks",
  "Likely Missing Documents",
  "Recommended Next Steps",
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

const PASS_TYPE_OPTIONS = [
  "Employment Pass",
  "S Pass",
  "EntrePass",
  "Dependent Pass",
  "Student Pass",
  "Long-Term Visit Pass",
];

const EDUCATION_OPTIONS = [
  "Secondary School",
  "Diploma",
  "Bachelor's Degree",
  "Master's Degree",
  "PhD",
];

const MARITAL_STATUS_OPTIONS = [
  "Single",
  "Married",
  "Engaged",
  "Divorced",
  "Widowed",
];

const LANGUAGE_OPTIONS = [
  "English",
  "English and Mandarin",
  "English and Malay",
  "English and Tamil",
  "Multilingual",
];

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

function buildPreviewPayload() {
  return {
    preview_target: "official",
  };
}

function createPreviewEntry(message) {
  return {
    status: "idle",
    message,
    data: null,
  };
}

function getCurrentStep(result, isLoading, previewState) {
  if (!isLoading) {
    if (result) {
      return "Assessment ready";
    }
    return "Waiting to start";
  }

  if (
    previewState.official.status === "starting" ||
    previewState.community.status === "starting"
  ) {
    return "Starting TinyFish live preview";
  }
  if (
    previewState.official.status === "live" ||
    previewState.community.status === "live"
  ) {
    return "Running readiness assessment";
  }
  if (
    previewState.official.status === "unavailable" &&
    previewState.community.status === "unavailable"
  ) {
    return "Continuing with fallback retrieval state";
  }
  return "Preparing analysis";
}

function getPreviewLabel(target) {
  return target === "official" ? "Official Scan" : "Community Scan";
}

function getPreviewStatusLabel(status) {
  if (status === "live") {
    return "Live";
  }
  if (status === "starting") {
    return "Starting";
  }
  if (status === "unavailable") {
    return "Unavailable";
  }
  if (status === "complete") {
    return "Complete";
  }
  return "Idle";
}

function getPreviewTimelineLabel(target, status) {
  const prefix = target === "official" ? "Official" : "Community";
  if (status === "live") {
    return `${prefix}: Live`;
  }
  if (status === "starting") {
    return `${prefix}: Starting`;
  }
  if (status === "unavailable") {
    return `${prefix}: Unavailable`;
  }
  if (status === "complete") {
    return `${prefix}: Complete`;
  }
  return `${prefix}: Standby`;
}

function getSourceProgress(status, hasData) {
  if (hasData || status === "complete" || status === "live") {
    return { percent: 100, tone: "complete", label: "Done" };
  }
  if (status === "starting") {
    return { percent: 35, tone: "starting", label: "Starting" };
  }
  if (status === "unavailable") {
    return { percent: 100, tone: "unavailable", label: "Fallback" };
  }
  return { percent: 0, tone: "idle", label: "Standby" };
}

function getEngineProgress(result, isLoading, previewState) {
  if (result) {
    return { percent: 100, tone: "complete", label: "Done" };
  }
  if (!isLoading) {
    return { percent: 0, tone: "idle", label: "Standby" };
  }
  if (
    previewState.official.status === "live" ||
    previewState.official.status === "unavailable" ||
    previewState.community.status === "starting" ||
    previewState.community.status === "live" ||
    previewState.community.status === "unavailable"
  ) {
    return { percent: 68, tone: "running", label: "Running" };
  }
  return { percent: 10, tone: "starting", label: "Waiting" };
}

function getDisplayedPreviewKey(previewState, isLoading) {
  if (!isLoading) {
    if (previewState.community.data?.streaming_url) {
      return "community";
    }
    if (previewState.official.data?.streaming_url) {
      return "official";
    }
    return "official";
  }

  if (previewState.community.status === "live") {
    return "community";
  }
  if (
    previewState.official.status === "live" ||
    previewState.official.status === "starting"
  ) {
    return "official";
  }
  if (previewState.community.status === "starting") {
    return "community";
  }
  return "official";
}

function getPreviewNarrative(previewState, isLoading, result) {
  if (isLoading) {
    if (previewState.official.status === "starting") {
      return "Scanning official ICA source";
    }
    if (
      previewState.official.status === "live" &&
      previewState.community.status !== "live"
    ) {
      return "Official scan in progress";
    }
    if (previewState.community.status === "starting") {
      return "Switching to community case source";
    }
    if (previewState.community.status === "live") {
      return "Scanning community case source";
    }
    return "Starting TinyFish retrieval";
  }

  if (result) {
    if (previewState.community.data?.streaming_url) {
      return "Community scan completed";
    }
    if (previewState.official.data?.streaming_url) {
      return "Official scan completed";
    }
    return "Assessment ready";
  }

  return "Ready for live preview";
}

function finalizePreviewEntries(current) {
  return {
    official:
      current.official.status === "live" && current.official.data
        ? { ...current.official, status: "complete" }
        : current.official,
    community:
      current.community.status === "live" && current.community.data
        ? { ...current.community, status: "complete" }
        : current.community,
  };
}

function getProgressStatus(result, isLoading) {
  if (isLoading) {
    return "Running";
  }
  if (result?.system_status?.analysis_mode === "demo_fallback") {
    return "Retrieval fallback";
  }
  if (result) {
    return "Complete";
  }
  return "Ready";
}

function getProgressStatusClass(result, isLoading) {
  const status = getProgressStatus(result, isLoading);
  if (status === "Running") {
    return "progress-status progress-status-running";
  }
  if (status === "Retrieval fallback") {
    return "progress-status progress-status-fallback";
  }
  if (status === "Complete") {
    return "progress-status progress-status-complete";
  }
  return "progress-status progress-status-ready";
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

function formatDimensionScore(score, maxScore) {
  return `${score}/${maxScore}`;
}

function formatScoreDelta(delta) {
  if (delta > 0) {
    return `+${delta}`;
  }
  return `${delta}`;
}

function getAdjustmentTone(direction) {
  if (direction === "up") {
    return "adjustment-pill adjustment-pill-up";
  }
  if (direction === "down") {
    return "adjustment-pill adjustment-pill-down";
  }
  return "adjustment-pill adjustment-pill-flat";
}

function formatSourceQuality(level) {
  if (!level) {
    return "Unknown";
  }
  return level.replace(/^\w/, (value) => value.toUpperCase());
}

function getSourceQualityClass(level) {
  if (level === "strong") {
    return "source-badge source-badge-strong";
  }
  if (level === "mixed") {
    return "source-badge source-badge-mixed";
  }
  if (level === "missing" || level === "thin") {
    return "source-badge source-badge-thin";
  }
  return "source-badge";
}

function getModeBanner(result) {
  const mode = result?.system_status?.analysis_mode;
  const retrievalMode = result?.system_status?.retrieval_mode;

  if (mode === "demo_fallback") {
    return {
      title: "Demo Fallback Mode",
      body: "Live services were unavailable, so the app switched to a stable structured demo response.",
      className: "mode-banner mode-banner-fallback",
    };
  }

  if (mode === "openai_only" || retrievalMode === "unavailable") {
    return {
      title: "OpenAI-Only Mode",
      body: "The analysis ran without TinyFish retrieval, so source-backed context is limited.",
      className: "mode-banner mode-banner-openai-only",
    };
  }

  if (mode === "retrieval_augmented") {
    return {
      title: "Retrieval-Augmented Mode",
      body: "The analysis used both model reasoning and retrieved source context.",
      className: "mode-banner mode-banner-live",
    };
  }

  return null;
}

function getScoreInterpretation(signal) {
  if (signal === "strong") {
    return "This profile looks well-positioned, with fewer major readiness gaps.";
  }
  if (signal === "low") {
    return "This profile appears early or incomplete, with several readiness gaps to address.";
  }
  return "This profile looks plausible but still has meaningful readiness gaps.";
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
  const [previewState, setPreviewState] = useState({
    official: createPreviewEntry(
      "Start an analysis to watch the official ICA browser session live.",
    ),
    community: createPreviewEntry(
      "Start an analysis to watch the community browser session live.",
    ),
  });
  const [sampleNotice, setSampleNotice] = useState("");
  const sampleTimerRef = useRef(null);
  const requestAbortRef = useRef(null);

  let scoreClass = "score-card";
  if (result?.eligibility_signal === "strong") {
    scoreClass = "score-card score-card-strong";
  } else if (result?.eligibility_signal === "low") {
    scoreClass = "score-card score-card-low";
  } else if (result?.eligibility_signal === "moderate") {
    scoreClass = "score-card score-card-moderate";
  }

  const modeBanner = getModeBanner(result);

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
    setSampleNotice("Sample profile loaded");
    window.clearTimeout(sampleTimerRef.current);
    sampleTimerRef.current = window.setTimeout(() => {
      setSampleNotice("");
    }, 2200);
  }

  function handleStopAnalysis() {
    requestAbortRef.current?.abort();
    requestAbortRef.current = null;
    setIsLoading(false);
    setErrorMessage("Analysis stopped. You can adjust the profile and run it again.");
    setPreviewState({
      official: createPreviewEntry(
        "Analysis was stopped before completion. Start another run when you're ready.",
      ),
      community: createPreviewEntry(
        "Analysis was stopped before completion. Start another run when you're ready.",
      ),
    });
  }

  async function startPreview(target, abortController) {
    setPreviewState((current) => ({
      ...current,
      [target]: {
        status: "starting",
        message:
          target === "official"
            ? "Launching TinyFish on the official ICA source."
            : "Launching TinyFish on the community case source.",
        data: null,
      },
    }));

    const response = await fetch(`${API_BASE_URL}/analyze/preview`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...buildPreviewPayload(),
        preview_target: target,
      }),
      signal: abortController.signal,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Preview failed with status ${response.status}`);
    }

    const previewData = await response.json();
    setPreviewState((current) => ({
      ...current,
      [target]: {
        status: "live",
        message:
          target === "official"
            ? "TinyFish is browsing the official ICA source."
            : "TinyFish is browsing the community case source.",
        data: previewData,
      },
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    requestAbortRef.current?.abort();
    const abortController = new AbortController();
    requestAbortRef.current = abortController;
    setResult(null);
    setIsLoading(true);
    setErrorMessage("");
    setPreviewState({
      official: createPreviewEntry("Launching TinyFish on the official ICA source."),
      community: createPreviewEntry(
        "Waiting to continue into the community case source.",
      ),
    });

    try {
      const payload = buildPayload(formState);
      await startPreview("official", abortController).catch((error) => {
        if (error?.name === "AbortError") {
          return;
        }
        setPreviewState((current) => ({
          ...current,
          official: {
            status: "unavailable",
            message: "Official preview was unavailable. The assessment can still continue.",
            data: null,
          },
        }));
        console.error(error);
      });

      const responsePromise = fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        signal: abortController.signal,
      });

      startPreview("community", abortController).catch((error) => {
        if (error?.name === "AbortError") {
          return;
        }
        setPreviewState((current) => ({
          ...current,
          community: {
            status: "unavailable",
            message: "Community preview was unavailable. The assessment can still continue.",
            data: null,
          },
        }));
        console.error(error);
      });

      const [response] = await Promise.all([responsePromise, delay(4500)]);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      if (error?.name === "AbortError") {
        return;
      }
      setErrorMessage(
        "We couldn’t reach the analysis service just now. Please retry when the backend is running.",
      );
      console.error(error);
    } finally {
      requestAbortRef.current = null;
      setPreviewState((current) => finalizePreviewEntries(current));
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Singapore PR Readiness</p>
        <h1>Assess Singapore PR readiness with official ICA guidance.</h1>
        <p className="hero-copy">
          Enter an applicant profile to generate a PR readiness score, risk
          summary, and recommended next steps, with community case patterns kept separate from official signals.
        </p>
        <div className="trust-strip">
          <span>Official ICA guidance is authoritative</span>
          <span>Community case patterns are anecdotal</span>
          <span>Race, religion, and ethnicity are not scoring variables</span>
        </div>
      </section>

      <section className="content-grid">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Applicant Profile</p>
              <h2>Profile Intake Form</h2>
              <p className="panel-subtitle">
                Structured profile intake for a Singapore PR readiness assessment.
              </p>
            </div>
            <div className="panel-actions">
              {sampleNotice ? (
                <span className="inline-notice">{sampleNotice}</span>
              ) : null}
              <button
                className="ghost-button"
                type="button"
                onClick={handleLoadSample}
              >
                Load Sample Profile
              </button>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group-title">Core Profile</div>
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

            <div className="form-group-title">Residency</div>
            <Field label="Years in SG">
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
              <select
                name="pass_type"
                value={formState.pass_type}
                onChange={handleChange}
                required
              >
                <option value="">Select pass type</option>
                {PASS_TYPE_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </Field>

            <div className="form-group-title">Employment</div>
            <Field label="Profession">
              <input
                name="profession"
                type="text"
                value={formState.profession}
                onChange={handleChange}
                required
              />
            </Field>

            <Field label="Salary / month (SGD)">
              <input
                min="0"
                name="monthly_salary"
                type="number"
                value={formState.monthly_salary}
                onChange={handleChange}
                required
              />
            </Field>

            <div className="form-group-title">Background</div>
            <Field label="Education">
              <select
                name="education"
                value={formState.education}
                onChange={handleChange}
                required
              >
                <option value="">Select education</option>
                {EDUCATION_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Marital Status">
              <select
                name="marital_status"
                value={formState.marital_status}
                onChange={handleChange}
                required
              >
                <option value="">Select status</option>
                {MARITAL_STATUS_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
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

            <div className="form-group-title">Application Context</div>
            <Field label="Prior PR Rejections">
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
              <select
                name="language_ability"
                value={formState.language_ability}
                onChange={handleChange}
                required
              >
                <option value="">Select language ability</option>
                {LANGUAGE_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
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
                placeholder="Add supporting context such as employment stability, family ties, or unusual circumstances."
              />
            </Field>
          </div>

          <div className="form-actions">
            <div className="action-row">
              <button className="primary-button" disabled={isLoading} type="submit">
              {isLoading ? "Analyzing..." : "Analyze Readiness"}
              </button>
              {isLoading ? (
                <button
                  className="ghost-button ghost-button-danger"
                  type="button"
                  onClick={handleStopAnalysis}
                >
                  Stop Analysis
                </button>
              ) : null}
            </div>
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
              <span className={getProgressStatusClass(result, isLoading)}>
                {getProgressStatus(result, isLoading)}
              </span>
            </div>

            {isLoading ? (
              <div className="loading-state">
                {(() => {
                  const displayedPreviewKey = getDisplayedPreviewKey(
                    previewState,
                    isLoading,
                  );
                  const displayedPreview = previewState[displayedPreviewKey];
                  const displayedLabel = getPreviewLabel(displayedPreviewKey);

                  return (
                    <>
                <div className="compact-progress-card">
                  <div className="compact-progress-topline">
                    <span className="compact-progress-label">Current step</span>
                    <strong>{getPreviewNarrative(previewState, isLoading, result)}</strong>
                  </div>
                  <div className="compact-progress-meta">
                    {[
                      {
                        name: "Official",
                        ...getSourceProgress(
                          previewState.official.status,
                          Boolean(previewState.official.data?.streaming_url),
                        ),
                      },
                      {
                        name: "Community",
                        ...getSourceProgress(
                          previewState.community.status,
                          Boolean(previewState.community.data?.streaming_url),
                        ),
                      },
                      {
                        name: "Engine",
                        ...getEngineProgress(result, isLoading, previewState),
                      },
                    ].map((item) => (
                      <div className="compact-progress-track" key={item.name}>
                        <div className="compact-progress-track-topline">
                          <span className="compact-progress-track-label">
                            {item.name}
                          </span>
                          <span className="compact-progress-track-value">
                            {item.label} · {item.percent}%
                          </span>
                        </div>
                        <div className="compact-progress-bar">
                          <span
                            className={`compact-progress-fill compact-progress-fill-${item.tone}`}
                            style={{ width: `${item.percent}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="preview-shell">
                  <div className="preview-header">
                    <span className="preview-kicker">TinyFish Live View</span>
                    <span className="preview-status preview-status-live">
                      {displayedLabel}
                    </span>
                  </div>
                  <div className="preview-sequence">
                    <span className="preview-sequence-pill">1. Official</span>
                    <span className="preview-sequence-pill">2. Community</span>
                  </div>
                  <div className="preview-pane">
                    <div className="preview-pane-header">
                      <span className="preview-pane-title">{displayedLabel}</span>
                      <span
                        className={`preview-status preview-status-${displayedPreview.status}`}
                      >
                        {getPreviewStatusLabel(displayedPreview.status)}
                      </span>
                    </div>
                    <p className="preview-message">{displayedPreview.message}</p>
                    {displayedPreviewKey === "community" ? (
                      <p className="preview-hint">
                        Community preview may take longer because it uses stealth browsing.
                      </p>
                    ) : null}
                    {displayedPreview.data?.streaming_url ? (
                      <iframe
                        className="preview-frame"
                        src={displayedPreview.data.streaming_url}
                        title={
                          displayedPreview.data.title ||
                          `${displayedLabel} live browser preview`
                        }
                      />
                    ) : (
                      <div className="preview-placeholder">
                        <span>
                          Live browser preview will appear here when TinyFish returns a
                          streaming URL.
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                    </>
                  );
                })()}
              </div>
            ) : (
              <div className="idle-state">
                {(() => {
                  const displayedPreviewKey = getDisplayedPreviewKey(
                    previewState,
                    isLoading,
                  );
                  const displayedPreview = previewState[displayedPreviewKey];
                  const hasCompletedPreview = Boolean(
                    previewState.official.data?.streaming_url ||
                      previewState.community.data?.streaming_url,
                  );
                  const displayedLabel = hasCompletedPreview
                    ? `${getPreviewLabel(displayedPreviewKey)} Playback`
                    : "Sequential TinyFish scan";

                  return (
                    <>
                <div className="compact-progress-card compact-progress-card-idle">
                  <div className="compact-progress-topline">
                    <span className="compact-progress-label">Pipeline</span>
                    <strong>{getPreviewNarrative(previewState, isLoading, result)}</strong>
                  </div>
                  <div className="compact-progress-meta">
                    {[
                      {
                        name: "Official",
                        ...getSourceProgress(
                          previewState.official.data?.streaming_url ? "complete" : "idle",
                          Boolean(previewState.official.data?.streaming_url),
                        ),
                      },
                      {
                        name: "Community",
                        ...getSourceProgress(
                          previewState.community.data?.streaming_url ? "complete" : "idle",
                          Boolean(previewState.community.data?.streaming_url),
                        ),
                      },
                      {
                        name: "Engine",
                        ...getEngineProgress(result, isLoading, previewState),
                      },
                    ].map((item) => (
                      <div className="compact-progress-track" key={item.name}>
                        <div className="compact-progress-track-topline">
                          <span className="compact-progress-track-label">
                            {item.name}
                          </span>
                          <span className="compact-progress-track-value">
                            {item.label} · {item.percent}%
                          </span>
                        </div>
                        <div className="compact-progress-bar">
                          <span
                            className={`compact-progress-fill compact-progress-fill-${item.tone}`}
                            style={{ width: `${item.percent}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="preview-shell preview-shell-idle">
                  <div className="preview-header">
                    <span className="preview-kicker">TinyFish Live View</span>
                    <span
                      className={`preview-status ${
                        hasCompletedPreview
                          ? "preview-status-complete"
                          : "preview-status-idle"
                      }`}
                    >
                      {hasCompletedPreview ? "Last playback" : "Sequential view"}
                    </span>
                  </div>
                  <div className="preview-sequence">
                    <span className="preview-sequence-pill">1. Official</span>
                    <span className="preview-sequence-pill">2. Community</span>
                  </div>
                  <div className="preview-pane">
                    <div className="preview-pane-header">
                      <span className="preview-pane-title">{displayedLabel}</span>
                      <span
                        className={`preview-status ${
                          hasCompletedPreview
                            ? "preview-status-complete"
                            : "preview-status-idle"
                        }`}
                      >
                        {hasCompletedPreview ? "Complete" : "Idle"}
                      </span>
                    </div>
                    {hasCompletedPreview ? (
                      <>
                        <p className="preview-message">
                          Last completed TinyFish playback from the retrieval pipeline.
                        </p>
                        {displayedPreviewKey === "community" ? (
                          <p className="preview-hint">
                            Community playback ran after the official ICA scan.
                          </p>
                        ) : (
                          <p className="preview-hint">
                            Official playback appears first in the retrieval sequence.
                          </p>
                        )}
                        <div className="preview-placeholder">
                          <div className="preview-mock">
                            <div className="preview-mock-bar">
                              <span className="preview-mock-chip">{displayedLabel}</span>
                              <span className="preview-status preview-status-complete">
                                Complete
                              </span>
                            </div>
                            <p>
                              Live playback is available during an active run. Start another
                              analysis to watch a fresh TinyFish browser session.
                            </p>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="preview-placeholder">
                        <div className="preview-mock">
                          <div className="preview-mock-bar">
                            <span className="preview-mock-chip">Sequential TinyFish scan</span>
                            <span className="preview-status preview-status-idle">Idle</span>
                          </div>
                          <p>
                            Start an analysis to watch TinyFish scan the official ICA source first and then continue to the community source in the same viewer.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                    </>
                  );
                })()}
              </div>
            )}
          </article>

          <article className="panel result-panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Assessment Output</p>
                <h2>Readiness Dashboard</h2>
                <p className="panel-subtitle">
                  Structured PR readiness output.
                </p>
              </div>
            </div>

            {result ? (
              <div className="result-content">
                <div className="hero-metrics">
                  <div className={scoreClass}>
                    <span className="score-label">Readiness Score</span>
                    <strong>{result.readiness_score}</strong>
                    <span className="score-scale">out of 100</span>
                    <p className="score-summary">
                      {getScoreInterpretation(result.eligibility_signal)}
                    </p>
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

                {modeBanner ? (
                  <div className={modeBanner.className}>
                    <p className="mode-banner-title">{modeBanner.title}</p>
                    <p>{modeBanner.body}</p>
                  </div>
                ) : null}

                <div className="featured-grid">
                  {["official_takeaways", "community_takeaways"].map((key) => {
                    const title =
                      key === "official_takeaways"
                        ? "Official ICA Takeaways"
                        : "Community Pattern Signals";

                    return (
                      <div className="featured-card" key={key}>
                        <h3>{title}</h3>
                        <ul>
                          {result[key]?.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>

                {result.scoring_breakdown ? (
                  <div className="breakdown-card">
                    <div className="breakdown-header">
                      <div>
                        <h3>Scoring Breakdown</h3>
                        <p>
                          Preliminary rubric score{" "}
                          <strong>
                            {result.scoring_breakdown.preliminary_score}
                          </strong>
                          . Final score{" "}
                          <strong>{result.scoring_breakdown.final_score}</strong>.
                        </p>
                      </div>
                    </div>
                    <div className="adjustment-card">
                      <div className="adjustment-header">
                        <span className="adjustment-title">Score Adjustment</span>
                        <span
                          className={getAdjustmentTone(
                            result.scoring_breakdown.score_adjustment?.direction,
                          )}
                        >
                          {formatScoreDelta(
                            result.scoring_breakdown.score_adjustment?.delta ?? 0,
                          )}
                        </span>
                      </div>
                      <p className="adjustment-reason">
                        {result.scoring_breakdown.score_adjustment?.reason}
                      </p>
                    </div>
                    {result.scoring_breakdown.source_quality ? (
                      <div className="source-quality-card">
                        <div className="source-quality-header">
                          <span className="adjustment-title">Source Quality</span>
                        </div>
                        <div className="source-quality-grid">
                          {["official", "community"].map((key) => {
                            const item = result.scoring_breakdown.source_quality?.[key];
                            if (!item) {
                              return null;
                            }

                            return (
                              <div className="source-quality-item" key={key}>
                                <div className="source-quality-topline">
                                  <span className="source-quality-label">
                                    {item.label}
                                  </span>
                                  <span className={getSourceQualityClass(item.level)}>
                                    {formatSourceQuality(item.level)}
                                  </span>
                                </div>
                                <p className="source-quality-reason">
                                  {item.reason}
                                </p>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ) : null}
                    <div className="breakdown-list">
                      {result.scoring_breakdown.dimensions?.map((dimension) => {
                        const width = Math.max(
                          6,
                          Math.min(
                            100,
                            (dimension.score / dimension.max_score) * 100,
                          ),
                        );

                        return (
                          <div className="breakdown-item" key={dimension.name}>
                            <div className="breakdown-topline">
                              <span className="breakdown-label">
                                {dimension.label}
                              </span>
                              <span className="breakdown-score">
                                {formatDimensionScore(
                                  dimension.score,
                                  dimension.max_score,
                                )}
                              </span>
                            </div>
                            <div
                              className="breakdown-bar"
                              aria-hidden="true"
                            >
                              <span style={{ width: `${width}%` }} />
                            </div>
                            <p className="breakdown-reason">
                              {dimension.reason}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : null}

                <div className="result-grid">
                  {SECTION_CONFIG.filter(
                    (section) =>
                      !["official_takeaways", "community_takeaways"].includes(
                        section.key,
                      ),
                  ).map((section) => (
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
                <p>Submit a profile to generate a readiness assessment.</p>
                <p>
                  The dashboard will surface a score, eligibility signal, major
                  strengths and risks, likely missing documents, and recommended next steps.
                </p>
                <div className="dashboard-preview-grid">
                  {DASHBOARD_PREVIEW.map((item) => (
                    <div className="dashboard-preview-card" key={item}>
                      <span className="dashboard-preview-title">{item}</span>
                      <span className="dashboard-preview-line short" />
                      <span className="dashboard-preview-line" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </article>
        </section>
      </section>
    </main>
  );
}

export default App;
