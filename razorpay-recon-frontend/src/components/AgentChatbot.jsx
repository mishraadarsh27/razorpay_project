import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, ShoppingBag, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function AgentChatbot() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI Sales Assistant. I can help you find products and process your payment instantly. What are you looking for today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const historyForApi = messages.map(m => ({
        role: m.role === 'assistant' ? 'assistant' : 'user',
        content: m.content
      })).filter(m => m.content); 

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          history: historyForApi
        })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I am having trouble connecting to the server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col lg:h-[650px] h-[500px] glass-card rounded-3xl overflow-hidden relative shadow-2xl shadow-purple-100/50 border border-white/60">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-xl p-5 border-b border-slate-100 flex items-center justify-between relative z-10">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-200">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-white rounded-full"></div>
          </div>
          <div>
            <h2 className="font-bold text-lg text-slate-800 flex items-center gap-2">
              Agentic Storefront <Sparkles className="w-4 h-4 text-purple-500" />
            </h2>
            <p className="text-xs font-semibold text-purple-600 uppercase tracking-wider">Powered by Gemini AI</p>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 scroll-smooth">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`} style={{animationDuration: '0.3s'}}>
            <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-gradient-to-br from-indigo-500 to-blue-600 text-white' : 'bg-white border border-slate-200 text-purple-600'}`}>
                {msg.role === 'user' ? <User className="w-5 h-5" /> : <ShoppingBag className="w-5 h-5" />}
              </div>
              <div className={`p-4 rounded-2xl shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-slate-100 text-slate-800 rounded-tl-none'}`}>
                <div className={`prose prose-sm prose-p:leading-relaxed max-w-none ${msg.role === 'user' ? 'text-white' : 'text-slate-700'}`}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown
                      components={{
                        a: ({node, ...props}) => (
                          <a {...props} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 mt-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold py-2.5 px-6 rounded-xl hover:shadow-lg hover:shadow-purple-200 hover:-translate-y-0.5 transition-all no-underline">
                            Buy via Razorpay
                          </a>
                        )
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    <p className="m-0 font-medium">{msg.content}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-fade-in-up">
            <div className="flex gap-3 max-w-[80%]">
              <div className="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 bg-white border border-slate-200 text-purple-600 shadow-sm">
                <Bot className="w-5 h-5" />
              </div>
              <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-sm rounded-tl-none flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-5 bg-white/80 backdrop-blur-xl border-t border-slate-100 relative z-10">
        <div className="flex gap-3 relative max-w-4xl mx-auto">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message here..."
            className="flex-1 bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all font-medium text-slate-700 shadow-inner"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-slate-900 text-white p-4 rounded-2xl hover:bg-slate-800 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none transition-all flex items-center justify-center aspect-square"
          >
            <Send className="w-5 h-5 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
}
