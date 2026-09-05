import { ShoppingBag, Sparkles } from 'lucide-react';
import AgentChatbot from './components/AgentChatbot';

function App() {
  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-100 via-slate-50 to-slate-200 text-slate-900 font-sans p-4 md:p-8 flex flex-col justify-center items-center">
      <div className="w-full max-w-6xl mx-auto space-y-8 animate-fade-in-up">
        {/* Header */}
        <header className="glass-card rounded-3xl p-6 flex flex-col md:flex-row justify-center md:justify-start items-center gap-6 shadow-xl shadow-indigo-100/50">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-200 relative overflow-hidden group">
              <div className="absolute inset-0 bg-white/20 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>
              <ShoppingBag className="w-7 h-7 text-white relative z-10" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-indigo-900 to-slate-800 flex items-center gap-2">
                Razorpay Storefront Agent <Sparkles className="w-6 h-6 text-purple-500" />
              </h1>
              <p className="text-sm text-slate-500 font-semibold tracking-wide uppercase mt-1">AI-Powered Shopping Experience</p>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          
          {/* Inventory Sidebar */}
          <div className="col-span-1 glass-card rounded-3xl p-8 lg:h-[700px] flex flex-col relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-purple-100/80 rounded-full blur-3xl opacity-50 -mr-20 -mt-20 transition-transform duration-700 group-hover:scale-125"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-indigo-100/80 rounded-full blur-3xl opacity-50 -ml-20 -mb-20 transition-transform duration-700 group-hover:scale-125"></div>
            
            <div className="flex-1 flex flex-col items-center text-center relative z-10">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-fuchsia-600 rounded-[2rem] flex items-center justify-center mb-6 shadow-xl shadow-purple-200 rotate-3 transition-all duration-500 group-hover:rotate-6 group-hover:scale-105">
                <ShoppingBag className="w-12 h-12 text-white" />
              </div>
              
              <h2 className="text-2xl font-bold mb-4 text-slate-800 tracking-tight">Hacker Store</h2>
              
              <p className="text-slate-500 mb-8 text-sm leading-relaxed font-medium px-2">
                Experience our conversational AI Sales Representative. 
                It recommends products, answers queries, and generates instant <span className="font-bold text-indigo-600">Razorpay</span> payment links.
              </p>
              
              <div className="w-full bg-white/70 backdrop-blur-md border border-slate-200/60 rounded-2xl p-6 text-left shadow-lg transition-transform duration-300 hover:-translate-y-1">
                <h3 className="font-bold text-xs uppercase tracking-widest mb-5 text-slate-800 flex items-center gap-2">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                  Live Inventory
                </h3>
                
                <ul className="text-sm font-medium text-slate-600 space-y-4">
                  {[
                    { name: "Razor T-Shirt", price: "₹500" },
                    { name: "Developer Hoodie", price: "₹1500" },
                    { name: "Mechanical Keyboard", price: "₹4500" },
                    { name: "Wireless Mouse", price: "₹1200" },
                    { name: "Coffee Mug", price: "₹300" }
                  ].map((item, i) => (
                    <li key={i} className="flex justify-between items-center group/item p-2 -mx-2 rounded-lg hover:bg-white transition-all cursor-default">
                      <span className="group-hover/item:text-indigo-600 transition-colors flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover/item:bg-indigo-500 transition-colors"></div>
                        {item.name}
                      </span> 
                      <span className="font-bold text-slate-900 group-hover/item:text-indigo-600 bg-slate-100 group-hover/item:bg-indigo-50 px-2 py-1 rounded-md transition-all">
                        {item.price}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
          
          {/* Chatbot Area */}
          <div className="col-span-1 lg:col-span-2 shadow-2xl shadow-indigo-200/40 rounded-3xl transition-transform duration-500 hover:-translate-y-1">
            <AgentChatbot />
          </div>
          
        </main>
      </div>
    </div>
  );
}

export default App;