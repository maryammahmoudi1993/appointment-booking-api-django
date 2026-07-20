export default function Footer() {
  return (
    <footer className="border-t border-brand-100 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-8 text-center text-sm text-gray-500 sm:px-6 lg:px-8">
        <p className="font-display font-semibold text-brand-800">
          Bloom Studio
        </p>
        <p className="mt-1">Calm, expert care — book in minutes.</p>
        <p className="mt-4 text-xs text-gray-400">
          &copy; {new Date().getFullYear()} Bloom Studio Booking System. All
          rights reserved.
        </p>
      </div>
    </footer>
  );
}
