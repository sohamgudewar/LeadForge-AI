import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [company, setCompany] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [leads, setLeads] = useState([]);

  const loadLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/leads`);

      setLeads(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const loadLead = async (leadId) => {
    try {
      const response = await axios.get(`${API_URL}/lead/${leadId}`);

      setResult(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const runAgent = async () => {
    if (!company) return;

    setLoading(true);

    try {
      let response;

      if (file) {
        const formData = new FormData();
        formData.append("company", company);
        formData.append("file", file);

        response = await axios.post(`${API_URL}/run-agent-with-pdf`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        response = await axios.post(`${API_URL}/run-agent`, {
          company,
        });
      }

      setResult(response.data);

      await loadLeads();
    } catch (error) {
      console.error(error);
      alert("Backend error");
    }

    setLoading(false);
  };

  useEffect(() => {
    loadLeads();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white">

      <div className="flex">

        {/* Sidebar */}

        <div className="w-72 min-h-screen bg-slate-800 p-4">

          <h2 className="text-2xl font-bold mb-4">
            Lead History
          </h2>

          <div className="space-y-2">

            {leads.map((lead) => (
              <button
                key={lead.id}
                onClick={() => loadLead(lead.id)}
                className="w-full text-left bg-slate-700 hover:bg-slate-600 p-3 rounded"
              >
                {lead.company}
              </button>
            ))}

          </div>

        </div>

        {/* Main Content */}

        <div className="flex-1 p-8">

          <h1 className="text-4xl font-bold mb-8">
            LeadForge AI
          </h1>

          <div className="bg-slate-800 p-6 rounded-xl mb-8">

            <input
              type="text"
              placeholder="Enter company name..."
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="w-full p-3 rounded text-black"
            />

            <div className="mt-3">
              <label className="block text-sm text-gray-400 mb-1">
                Optional: Upload company PDF for better personalization
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files[0] || null)}
                className="w-full text-sm text-gray-400 file:mr-3 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
              />
            </div>

            <button
              onClick={runAgent}
              className="mt-4 px-6 py-3 bg-blue-600 rounded"
            >
              {loading
                ? "Generating..."
                : "Generate Outreach"}
            </button>

            {loading && (
              <p className="mt-4 text-yellow-400 text-sm">
                This may take a minute as 7+ AI agents analyze the company...
              </p>
            )}

          </div>

          {result && (
            <div className="space-y-6">

              <div className="bg-slate-800 p-6 rounded-xl">
                <h2 className="text-2xl font-bold mb-2">
                  Research
                </h2>

                <pre className="whitespace-pre-wrap">
                  {result.research}
                </pre>
              </div>

              {result.lead_score && (
                <div className="bg-slate-800 p-6 rounded-xl">
                  <h2 className="text-2xl font-bold mb-2">
                    Lead Score
                  </h2>

                  <pre className="whitespace-pre-wrap">
                    {result.lead_score}
                  </pre>
                </div>
              )}

              <div className="bg-slate-800 p-6 rounded-xl">
                <h2 className="text-2xl font-bold mb-2">
                  Personalization
                </h2>

                <pre className="whitespace-pre-wrap">
                  {result.personalization}
                </pre>
              </div>

              <div className="bg-slate-800 p-6 rounded-xl">
                <h2 className="text-2xl font-bold mb-2">
                  Email
                </h2>

                <pre className="whitespace-pre-wrap">
                  {result.email}
                </pre>
              </div>
              <div className="bg-slate-800 p-6 rounded-xl">
                <h2 className="text-2xl font-bold mb-2">
                  Follow-Up Sequence
                </h2>

                <pre className="whitespace-pre-wrap">
                  {result.followups}
                </pre>
              </div>
            </div>
          )}

        </div>

      </div>

      <div className="fixed bottom-4 right-4 text-sm text-gray-500">
        Contact developer:{" "}
        <a href="mailto:sohamgudewar10@gmail.com" className="text-blue-400 hover:underline">
          sohamgudewar10@gmail.com
        </a>
      </div>

    </div>
  );
}

export default App;