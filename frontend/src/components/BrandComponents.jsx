import { Brain } from "lucide-react";

export const BrandLockup = ({ 
  showSubtitle = false, 
  size = 'default',
  variant = 'default',
  className = ''
}) => {
  const sizes = {
    small: { icon: 'w-8 h-8', iconInner: 'w-4 h-4', title: 'text-lg', subtitle: 'text-[10px]' },
    default: { icon: 'w-10 h-10', iconInner: 'w-6 h-6', title: 'text-xl', subtitle: 'text-xs' },
    large: { icon: 'w-12 h-12', iconInner: 'w-7 h-7', title: 'text-2xl', subtitle: 'text-sm' },
    hero: { icon: 'w-16 h-16', iconInner: 'w-10 h-10', title: 'text-4xl', subtitle: 'text-base' }
  };
  
  const s = sizes[size] || sizes.default;
  
  if (variant === 'stacked') {
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="brand-lockup-stacked">
        <div className={`${s.icon} rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center mb-2`}>
          <Brain className={`${s.iconInner} text-white`} />
        </div>
        <span className={`${s.title} font-bold font-['Outfit'] tracking-tight`}>My-AlphaAI</span>
        {showSubtitle && (
          <span className={`${s.subtitle} text-zinc-400 font-light tracking-[0.2em] uppercase mt-1`}>
            Signal Intelligence System
          </span>
        )}
      </div>
    );
  }
  
  return (
    <div className={`flex items-center gap-3 ${className}`} data-testid="brand-lockup">
      <div className={`${s.icon} rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center`}>
        <Brain className={`${s.iconInner} text-white`} />
      </div>
      <div className="flex flex-col">
        <span className={`${s.title} font-bold font-['Outfit'] tracking-tight leading-none`}>My-AlphaAI</span>
        {showSubtitle && (
          <span className={`${s.subtitle} text-zinc-400 font-light tracking-[0.15em] uppercase`}>
            Signal Intelligence System
          </span>
        )}
      </div>
    </div>
  );
};

export const PoweredByTag = ({ className = '' }) => (
  <div className={`flex items-center justify-center gap-2 text-xs text-zinc-500 ${className}`} data-testid="powered-by-tag">
    <span className="opacity-60">Powered by the</span>
    <span className="text-[#7B61FF] font-medium">My-AlphaAI</span>
    <span className="opacity-60">Signal Intelligence System</span>
  </div>
);
