import Link from 'next/link'

const navItems = [
  { label: 'Odds', href: '/odds' },
  { label: 'My Bets', href: '/bets' },
  { label: 'Analytics', href: '/analytics' },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-neutral-800">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link href="/odds" className="text-lg font-bold tracking-tight">
            Packing Report
          </Link>
          <ul className="flex gap-6 text-sm">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-neutral-400 transition-colors hover:text-neutral-100">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        {children}
      </main>
    </div>
  )
}
