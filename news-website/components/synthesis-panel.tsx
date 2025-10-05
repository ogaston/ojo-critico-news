import { DebateSynthesis } from '../types';
import { formatDate, formatProbability, splitParagraphs } from '../lib/format';

interface SynthesisPanelProps {
  synthesis: DebateSynthesis | null;
}

function resolveVerdict(data: DebateSynthesis | null): string {
  if (!data) {
    return 'Awaiting verdict';
  }

  return (
    data.verdict ||
    (data.synthesis_report && data.synthesis_report.verdict) ||
    (data.analysis_report && data.analysis_report.verdict) ||
    'Unclear'
  );
}

function resolveProbability(data: DebateSynthesis | null): string {
  if (!data) {
    return '—';
  }

  const probability =
    data.probability_true ??
    (data.analysis_report ? (data.analysis_report.prob_true as number | undefined) : undefined);

  return formatProbability(probability || null);
}

function resolveReport(data: DebateSynthesis | null): string[] {
  if (!data) {
    return [];
  }

  const report =
    data.report || (data.synthesis_report ? data.synthesis_report.report : undefined);

  if (report) {
    return splitParagraphs(report);
  }

  if (data.analysis_report && typeof data.analysis_report.rationale === 'string') {
    return splitParagraphs(data.analysis_report.rationale);
  }

  if (data.analysis_report && typeof data.analysis_report.raw_analysis === 'string') {
    return splitParagraphs(data.analysis_report.raw_analysis);
  }

  return [];
}

export function SynthesisPanel({ synthesis }: SynthesisPanelProps) {
  const verdict = resolveVerdict(synthesis);
  const probability = resolveProbability(synthesis);
  const reportParagraphs = resolveReport(synthesis);
  const stamped = synthesis && synthesis.created_at ? formatDate(synthesis.created_at) : null;

  return (
    <aside className="sticky top-8 space-y-6 rounded-sm border border-ink/10 bg-white p-6">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.35em] text-ink/50">Debate Synthesis</p>
        <h2 className="font-serif text-2xl text-ink">Critical Verdict</h2>
      </header>

      <div className="flex items-center justify-between rounded-sm border border-ink/10 bg-parchment p-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-ink/50">Verdict</p>
          <p className="mt-1 font-serif text-xl text-ink">{verdict}</p>
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-[0.3em] text-ink/50">Probability True</p>
          <p className="mt-1 font-serif text-xl text-ink">{probability}</p>
        </div>
      </div>

      {reportParagraphs.length > 0 ? (
        <div className="space-y-4 text-sm leading-relaxed text-ink/80">
          {reportParagraphs.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
      ) : (
        <p className="text-sm leading-relaxed text-ink/60">
          The debate team has not submitted a synthesis for this article yet. Refresh the newsroom once the
          autonomous agents complete their review.
        </p>
      )}

      <footer className="border-t border-ink/10 pt-4 text-xs uppercase tracking-[0.2em] text-ink/50">
        <div className="flex items-center justify-between">
          <span>Status</span>
          <span>{synthesis ? 'Filed' : 'Pending'}</span>
        </div>
        {stamped && (
          <div className="mt-2 flex items-center justify-between">
            <span>Filed On</span>
            <span>{stamped}</span>
          </div>
        )}
      </footer>
    </aside>
  );
}
