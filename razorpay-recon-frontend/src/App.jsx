import { useState, useEffect, useRef } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Upload, Activity, AlertTriangle, Download, FileText } from 'lucide-react';
import Papa from 'papaparse';

function App() {
  const [file, setFile] = useState(null);
  const [batchId, setBatchId] = useState(null);
  const [status, setStatus] = useState('Idle');
  const [metrics, setMetrics] = useState(null);
  const [results, setResults] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://127.0.0.1:8000/ws');
    
    ws.current.onopen = () => {
      console.log('Connected to WebSocket');
      ws.current.send('ping'); 
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'progress') {
        setStatus(data.message);
      } else if (data.type === 'complete') {
        setStatus('Reconciliation Complete! ✅');
        setMetrics(data.metrics);
        setResults(data.results);
      }
    };

    return () => ws.current.close();
  }, []);

  const handleUpload = async () => {
    if (!file) return alert('Please select a CSV file first!');
    
    const formData = new FormData();
    formData.append('file', file);

    setStatus('Uploading dataset...');
    const response = await fetch('http://127.0.0.1:8000/upload', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    setBatchId(data.batch_id);
    setStatus(`Uploaded successfully! Batch ID: ${data.batch_id.substring(0, 8)}...`);
  };

  const handleProcess = async () => {
    if (!batchId) return;
    setStatus('Processing started... Listen to live updates!');
    await fetch(`http://127.0.0.1:8000/process/${batchId}`, { method: 'POST' });
  };

  const downloadExceptions = () => {
    const exceptions = results.filter(r => r.status === 'EXCEPTION');
    const csv = Papa.unparse(exceptions);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'exceptions_report.csv';
    link.click();
  };

  const pieData = metrics ? [
    { name: 'Matched', value: metrics.matched, color: '#10b981' }, 
    { name: 'Exceptions', value: metrics.exceptions, color: '#ef4444' } 
  ] : [];

  const barData = results.slice(0, 10).map(r => ({
    name: r.internal_id,
    score: r.confidence_score,
    status: r.status
  }));

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto">
      <div className="mb-8 flex items-center gap-3">
        <Activity className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-800">Razorpay Reconciliation Engine</h1>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-500" /> 1. Upload Dataset (CSV)
        </h2>
        <div className="flex gap-4 items-end">
          <input 
            type="file" 
            accept=".csv" 
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <button 
            onClick={handleUpload}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2 transition"
          >
            <Upload className="w-4 h-4" /> Upload
          </button>
          {batchId && (
            <button 
              onClick={handleProcess}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2 transition"
            >
              <Activity className="w-4 h-4" /> Process
            </button>
          )}
        </div>
        {status !== 'Idle' && (
          <div className="mt-4 p-3 bg-blue-50 text-blue-800 rounded-lg text-sm font-medium animate-pulse">
            Status: {status}
          </div>
        )}
      </div>

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Match Rate Overview</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center mt-2">
              <span className="text-3xl font-bold text-gray-800">{metrics.match_rate}%</span>
              <p className="text-gray-500 text-sm">Overall Match Rate</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Top 10 Confidence Scores</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={barData}>
                <XAxis dataKey="name" tick={{fontSize: 12}} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.status === 'EXCEPTION' ? '#ef4444' : '#10b981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" /> Exception List (Unresolved)
            </h3>
            <button 
              onClick={downloadExceptions}
              className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg flex items-center gap-2 transition"
            >
              <Download className="w-4 h-4" /> Download CSV
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-600 uppercase">
                <tr>
                  <th className="px-4 py-3">Internal ID</th>
                  <th className="px-4 py-3">Bank ID</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">AI Agent Analysis 🤖</th>
                </tr>
              </thead>
              <tbody>
                {results.filter(r => r.status === 'EXCEPTION').map((row, idx) => (
                  <tr key={idx} className="border-b hover:bg-red-50 transition">
                    <td className="px-4 py-3 font-medium">{row.internal_id}</td>
                    <td className="px-4 py-3 text-gray-500">{row.bank_id || 'Unmatched'}</td>
                    <td className="px-4 py-3">
                      <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-bold">
                        {row.confidence_score}%
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {row.ai_analysis ? (
                        <div className="text-xs text-gray-700 bg-blue-50 p-2 rounded-lg border border-blue-200">
                          <span className="font-semibold text-blue-700 block mb-1">🤖 AI Agent:</span>
                          {row.ai_analysis}
                        </div>
                      ) : (
                        <span className="text-gray-400 italic">Analyzing...</span>
                      )}
                    </td>
                  </tr>
                ))}
                {results.filter(r => r.status === 'EXCEPTION').length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-4 py-8 text-center text-green-600 font-medium">
                      🎉 Perfect! No exceptions found. All records matched.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;