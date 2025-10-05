export default function Loading() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-12 w-3/5 bg-ink/10" />
      <div className="grid gap-6 md:grid-cols-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="space-y-4 border border-ink/10 bg-white p-6">
            <div className="h-48 bg-ink/10" />
            <div className="h-6 w-3/4 bg-ink/10" />
            <div className="h-5 w-full bg-ink/10" />
            <div className="h-5 w-4/5 bg-ink/10" />
          </div>
        ))}
      </div>
    </div>
  );
}
