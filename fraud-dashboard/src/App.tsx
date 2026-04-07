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
      <nav className="sticky top-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-gray-800/80 px-6 py-3 shadow-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-purple-600 to-blue-500 p-1.5 rounded-lg shadow-lg">
            <ShieldCheck size={20} className="text-white" />
          </div>
          <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-400 tracking-tight">
            Antigravity Fraud Intelligence
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1 bg-red-500/10 border border-red-500/20 text-red-500 text-xs font-semibold rounded-md flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-red-400"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            LIVE
          </div>
          <div className="h-6 w-8 rounded bg-gray-800 border border-gray-700 animate-pulse hidden sm:block"></div>
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
