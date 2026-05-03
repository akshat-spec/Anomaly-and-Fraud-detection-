import { ShieldCheck, Activity, LayoutDashboard, Bell, Brain, FileText, Code } from "lucide-react";
import { LiveTransactionFeed } from "./components/LiveTransactionFeed";
import { FraudRateChart } from "./components/FraudRateChart";
import { MetricCards } from "./components/MetricCards";
import { AlertPanel } from "./components/AlertPanel";
import { ModelHealth } from "./components/ModelHealth";

function App() {
  return (
    <div className="min-h-screen bg-[#050505] text-slate-200 font-sans antialiased selection:bg-indigo-500/30">
      {/* Premium Industrial Header */}
      <header className="sticky top-0 z-50 bg-black/40 backdrop-blur-2xl border-b border-white/5 px-8 py-5 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShieldCheck size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-white leading-tight tracking-tight">
                FRAUD <span className="text-indigo-400">DETECTION</span>
              </h1>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></span>
                <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase">Intelligent Protection Active</p>
              </div>
            </div>
          </div>
          
          <div className="hidden md:flex h-8 w-px bg-white/10"></div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="flex items-center gap-2 text-xs font-bold text-white tracking-widest uppercase border-b-2 border-indigo-500 pb-0.5">
              <LayoutDashboard size={14} /> Overview
            </a>
            <a href="#" className="flex items-center gap-2 text-xs font-bold text-slate-500 tracking-widest uppercase hover:text-white transition-colors">
              <Bell size={14} /> Alerts
            </a>
            <a href="#" className="flex items-center gap-2 text-xs font-bold text-slate-500 tracking-widest uppercase hover:text-white transition-colors">
              <Brain size={14} /> Models
            </a>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-full flex items-center gap-3">
            <div className="flex -space-x-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="w-6 h-6 rounded-full border-2 border-black bg-slate-800" />
              ))}
            </div>
            <span className="text-[11px] font-bold text-slate-400 tracking-tight">Ops Team Online</span>
          </div>
        </div>
      </header>

      {/* Industrial Layout Content */}
      <main className="max-w-[1600px] mx-auto px-8 py-8">
        
        {/* Welcome Section */}
        <div className="mb-10">
          <h2 className="text-3xl font-black text-white tracking-tighter mb-2">Platform Summary</h2>
          <p className="text-slate-500 text-sm font-medium">Real-time inference monitoring and anomaly detection engine.</p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-12 gap-8">
          
          {/* Key Performance Indicators */}
          <div className="col-span-12">
            <MetricCards />
          </div>

          {/* Core Monitoring Area */}
          <div className="col-span-12 lg:col-span-8 space-y-8">
            <div className="glass-card rounded-3xl overflow-hidden">
              <LiveTransactionFeed />
            </div>
            
            <div className="grid grid-cols-2 gap-8">
              <div className="col-span-2 md:col-span-1">
                <AlertPanel />
              </div>
              <div className="col-span-2 md:col-span-1">
                <FraudRateChart />
              </div>
            </div>
          </div>

          {/* Sidebar / Health Area */}
          <div className="col-span-12 lg:col-span-4 space-y-8">
            <ModelHealth />
            
            {/* Quick Actions / Help Card */}
            <div className="bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-3xl p-8 relative overflow-hidden group">
              <div className="relative z-10">
                <h3 className="text-xl font-bold text-white mb-4">Need Assistance?</h3>
                <p className="text-slate-300 text-sm mb-6 leading-relaxed">
                  Our system is currently processing thousands of signals per second. Check our documentation for tuning thresholds.
                </p>
                <button className="flex items-center justify-center gap-3 w-full px-6 py-3 bg-white text-black font-bold text-xs uppercase tracking-widest rounded-xl hover:bg-slate-200 transition-all active:scale-95">
                  <FileText size={16} /> View Documentation
                </button>
              </div>
              <Activity className="absolute -right-8 -bottom-8 w-48 h-48 text-indigo-500/10 -rotate-12 group-hover:scale-110 transition-transform duration-700" />
            </div>
          </div>

        </div>
      </main>
      
      {/* Footer Status */}
      <footer className="fixed bottom-0 left-0 right-0 h-10 bg-black/80 backdrop-blur-md border-t border-white/5 flex items-center justify-between px-8 z-50">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">API: Connected</span>
          </div>
          <div className="w-px h-3 bg-white/10"></div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Models: Loaded</span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-[10px] font-bold text-slate-600 uppercase tracking-[0.2em]">
          <div className="flex items-center gap-1 text-indigo-400">
            <Code size={12} /> Made by Akshat
          </div>
          <div className="w-px h-3 bg-white/10"></div>
          &copy; 2026 Intelligence Corp
        </div>
      </footer>

    </div>
  );
}

export default App;
