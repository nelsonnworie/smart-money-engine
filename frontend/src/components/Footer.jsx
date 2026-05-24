import { useTheme } from '../context/ThemeContext'

function TelegramIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
    </svg>
  )
}

function XIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  )
}

function GithubIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
    </svg>
  )
}

function renderLinkIcon(icon) {
  if (icon === 'tg') return <TelegramIcon />
  if (icon === 'x') return <XIcon />
  if (icon === 'gh') return <GithubIcon />
  return null
}

const sections = [
  {
    title: 'Product',
    links: [
      { label: 'Signal Feed', href: '#' },
      { label: 'Clusters', href: '#' },
      { label: 'Wallet Explorer', href: '#' },
      { label: 'Top Movers', href: '#' },
    ],
  },
  {
    title: 'Community',
    links: [
      { label: 'Twitter / X', href: '#', icon: 'x' },
      { label: 'Telegram', href: '#', icon: 'tg' },
      { label: 'Telegram Bot', href: '#', icon: 'tg' },
      { label: 'GitHub', href: '#', icon: 'gh' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Terms of Service', href: '#' },
      { label: 'Privacy Policy', href: '#' },
      { label: 'Disclaimer', href: '#' },
      { label: 'Contact', href: '#' },
    ],
  },
]

const footerStats = [
  { label: 'Chains', value: '14+' },
  { label: 'Signals', value: '2.8K' },
  { label: 'Wallets', value: '50K+' },
]

const topGlow = { background: 'linear-gradient(90deg, transparent, rgba(0,212,170,0.3), transparent)' }
const radialGlow = { background: 'radial-gradient(ellipse at top, rgba(0,212,170,0.04) 0%, transparent 70%)' }
const logoBox = { background: 'linear-gradient(135deg, rgba(0,212,170,0.2), rgba(0,212,170,0.05))', border: '1px solid rgba(0,212,170,0.2)' }

export default function Footer() {
  const { isDark } = useTheme()

  const footerClass = `relative border-t flex-shrink-0 transition-colors duration-300 w-full ${
    isDark ? 'border-dark-700/30 bg-dark-900/95' : 'border-light-200 bg-white/95'
  }`
  const statValClass = isDark ? 'text-sm font-bold font-mono text-dark-100' : 'text-sm font-bold font-mono text-light-800'
  const statLblClass = isDark ? 'text-[9px] uppercase tracking-wide text-dark-400' : 'text-[9px] uppercase tracking-wide text-light-400'
  const bottomClass = isDark
    ? 'pt-6 border-t flex flex-col sm:flex-row items-center justify-between gap-3 border-dark-700/30'
    : 'pt-6 border-t flex flex-col sm:flex-row items-center justify-between gap-3 border-light-200'
  const copyClass = isDark ? 'text-[11px] font-mono text-dark-400' : 'text-[11px] font-mono text-light-400'

  return (
    <footer className={footerClass}>
      <div className="absolute top-0 left-0 right-0 h-px" style={topGlow} />
      <div className="absolute top-0 left-0 right-0 h-16 pointer-events-none" style={radialGlow} />

      <div className="w-full px-8 pt-12 pb-8">
        <div className="max-w-screen-2xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-x-12 gap-y-10 mb-10">
            {/* Column 1: Logo + Stats + Description */}
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={logoBox}>
                  <img src="/vite.svg" alt="SME" className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-bold leading-tight">
                    <span style={{ color: '#00d4aa' }}>Smart Money</span>
                    <span style={{ color: '#f59e0b' }}> Engine</span>
                  </p>
                </div>
              </div>

              <p className={`text-xs leading-relaxed ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                Cross-Chain Signal Platform
              </p>

              <div className="flex items-center gap-4">
                {footerStats.map(stat => (
                  <div key={stat.label}>
                    <p className={statValClass}>{stat.value}</p>
                    <p className={statLblClass}>{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Columns 2-3: Product, Community */}
            {sections.slice(0, 2).map(section => {
              const headClass = isDark
                ? 'text-[10px] font-bold uppercase tracking-widest mb-5 text-dark-200'
                : 'text-[10px] font-bold uppercase tracking-widest mb-5 text-light-700'
              return (
                <div key={section.title}>
                  <h4 className={headClass}>{section.title}</h4>
                  <ul className="space-y-3">
                    {section.links.map(link => {
                      const linkIcon = link.icon ? renderLinkIcon(link.icon) : null
                      const linkClass = isDark
                        ? 'inline-flex items-center gap-2 text-sm transition-all duration-150 group text-dark-300 hover:text-brand-400'
                        : 'inline-flex items-center gap-2 text-sm transition-all duration-150 group text-light-500 hover:text-brand-600'
                      return (
                        <li key={link.label}>
                          <a href={link.href} className={linkClass}>
                            {linkIcon && (
                              <span className="opacity-60 group-hover:opacity-100 transition-opacity">{linkIcon}</span>
                            )}
                            <span>{link.label}</span>
                          </a>
                        </li>
                      )
                    })}
                  </ul>
                </div>
              )
            })}

            {/* Column 4: Legal */}
            <div>
              <h4 className={`text-[10px] font-bold uppercase tracking-widest mb-5 ${
                isDark ? 'text-dark-200' : 'text-light-700'
              }`}>Legal</h4>
              <ul className="space-y-3">
                {sections[2].links.map(link => {
                  const linkClass = isDark
                    ? 'inline-flex items-center gap-2 text-sm transition-all duration-150 group text-dark-300 hover:text-brand-400'
                    : 'inline-flex items-center gap-2 text-sm transition-all duration-150 group text-light-500 hover:text-brand-600'
                  return (
                    <li key={link.label}>
                      <a href={link.href} className={linkClass}>
                        <span>{link.label}</span>
                      </a>
                    </li>
                  )
                })}
              </ul>
            </div>
          </div>

          <div className={bottomClass}>
            <p className={copyClass}>
              &copy; 2026 Smart Money Engine. All rights reserved.
            </p>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse-glow" />
              <span className={copyClass}>All systems operational</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}