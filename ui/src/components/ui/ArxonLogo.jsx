import { cn } from '@/lib/utils'

const ArxonLogo = ({ size = 'md', className }) => {
  const sizes = {
    sm: 'w-7 h-7 text-[10px]',
    md: 'w-8 h-8 text-xs',
    lg: 'w-10 h-10 text-sm',
  }

  return (
    <div
      className={cn(
        'relative flex items-center justify-center shrink-0',
        sizes[size],
        className
      )}
    >
      <div className="absolute inset-0 rotate-45 rounded-sm border border-arx-blue/60 bg-arx-blue/10 shadow-[0_0_12px_rgba(59,130,246,0.4)]" />
      <span className="relative z-10 font-bold text-arx-blue">A</span>
    </div>
  )
}

export default ArxonLogo
