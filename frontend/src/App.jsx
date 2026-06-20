import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [company, setCompany] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [leads, setLeads] = useState([]);

  const loadLeads = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/leads"
      );

      setLeads(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const loadLead = async (leadId) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/lead/${leadId}`
      );

      setResult(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const runAgent = async () => {
    if (!company) return;

    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/run-agent",
        {
          company,
        }
      );

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

            <button
              onClick={runAgent}
              className="mt-4 px-6 py-3 bg-blue-600 rounded"
            >
              {loading
                ? "Generating..."
                : "Generate Outreach"}
            </button>

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

    </div>
  );
}

export default App;