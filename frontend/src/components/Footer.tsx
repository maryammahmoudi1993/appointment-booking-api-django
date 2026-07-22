export default function Footer() {
  return (
    <footer className="border-t border-brand-100 bg-white" role="contentinfo">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
          <div className="text-center sm:text-left">
            <p className="font-display font-semibold text-brand-800">
              BloomFlow AI
            </p>
            <p className="mt-1 text-sm text-gray-500">
              Smart booking &amp; revenue copilot for small businesses.
            </p>
          </div>
          <nav aria-label="Footer navigation" className="flex gap-4 text-sm">
            <a href="/services" className="text-gray-500 hover:text-brand-700 transition-colors">
              Services
            </a>
            <a href="/staff" className="text-gray-500 hover:text-brand-700 transition-colors">
              Staff
            </a>
            <a href="/api/docs/" className="text-gray-500 hover:text-brand-700 transition-colors" target="_blank" rel="noopener noreferrer">
              API Docs
            </a>
          </nav>
        </div>
        <p className="mt-6 text-center text-xs text-gray-400">
          &copy; {new Date().getFullYear()} BloomFlow AI. Built with Django, React, and OpenAI.
        </p>
      </div>
    </footer>
  );
}
