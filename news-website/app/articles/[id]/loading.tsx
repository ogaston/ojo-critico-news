export default function ArticleLoading() {
  return (
    <div className="grid gap-12 lg:grid-cols-[2fr_1fr]">
      <div className="space-y-6">
        <div className="h-10 w-1/2 bg-ink/10" />
        <div className="h-16 w-4/5 bg-ink/10" />
        <div className="h-6 w-2/5 bg-ink/10" />
        <div className="h-96 w-full bg-ink/10" />
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="h-6 w-full bg-ink/10" />
          ))}
        </div>
      </div>
      <div className="space-y-4">
        <div className="h-10 w-1/2 bg-ink/10" />
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-5 w-full bg-ink/10" />
          ))}
        </div>
      </div>
    </div>
  );
}
