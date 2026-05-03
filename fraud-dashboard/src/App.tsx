import { ShieldCheck } from "lucide-react";
import { LiveTransactionFeed } from "./components/LiveTransactionFeed";
import { FraudRateChart } from "./components/FraudRateChart";
import { MetricCards } from "./components/MetricCards";
import { AlertPanel } from "./components/AlertPanel";
import { ModelHealth } from "./components/ModelHealth";

function App() {
  return (
    <div className="min-h-screen bg-[#050505] text-gray-200 font-sans selection:bg-purple-500/30">
      
      {/* Top Navbar */}
      <nav className="sticky top-0 z-50 bg-black/60 backdrop-blur-xl border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-2 rounded-xl shadow-lg shadow-purple-500/20">
            <ShieldCheck size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Fraud Detection
            </h1>
            <p className="text-[10px] text-purple-400 font-bold tracking-[0.2em] uppercase">Intelligence Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-3 py-1.5 bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] font-bold rounded-full flex items-center gap-2 tracking-wider">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-red-400"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            SYSTEM LIVE
          </div>
          <div className="w-8 h-8 rounded-full bg-gradient-to-b from-gray-700 to-gray-900 border border-white/10 hidden sm:block"></div>
        </div>
      </nav>

      {/* Main Dashboard Layout */}
      <main className="max-w-7xl mx-auto p-4 md:p-6 lg:p-8 flex flex-col gap-6 pb-20">
        
        {/* Tier 1: Core Metrics Overview */}
        <section className="w-full">
          <MetricCards />
        </section>

        {/* Tier 2: Real-time Streams & Model Health */}
        <section className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <LiveTransactionFeed />
          </div>
          <div className="lg:col-span-1">
            <ModelHealth />
          </div>
        </section>

        {/* Tier 3: Analytics & Manual Review */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <FraudRateChart />
          </div>
          <div className="lg:col-span-2">
            <AlertPanel />
          </div>
        </section>

      </main>

    </div>
  );
}

export default App;
