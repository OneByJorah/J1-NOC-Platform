import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function WazuhSIEM() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wazuhStatus, setWazuhStatus] = useState<string>('Checking...');
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [ollamaStatus, setOllamaStatus] = useState<string>('Checking...');
  const [ollamaModel, setOllamaModel] = useState('llama3.2:1b');
  const [prompt, setPrompt] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    // Load Wazuh data
    const loadWazuhData = async () => {
      try {
        setLoading(true);
        
        // Check Wazuh status
        try {
          const statusResponse = await fetch('/api/wazuh/status');
          if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            setWazuhStatus(statusData.status || 'Connected');
          } else {
            setWazuhStatus('Disconnected');
          }
        } catch (err) {
          setWazuhStatus('Disconnected');
        }
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock alerts data
        const mockAlerts = [
          { id: 1, timestamp: '2026-06-15T14:30:22Z', rule: 'SSH brute force attempt', level: 10, agent: 'webserver-01', location: '/var/log/auth.log' },
          { id: 2, timestamp: '2026-06-15T14:28:15Z', rule: 'Multiple failed logins', level: 8, agent: 'appserver-02', location: '/var/log/auth.log' },
          { id: 3, timestamp: '2026-06-15T14:25:43Z', rule: 'Suspicious network activity', level: 12, agent: 'dbserver-01', location: '/var/log/syslog' },
          { id: 4, timestamp: '2026-06-15T14:22:11Z', rule: 'File integrity checksum changed', level: 7, agent: 'webserver-01', location: '/etc/passwd' },
          { id: 5, timestamp: '2026-06-15T14:18:37Z', rule: 'Possible SQL injection attempt', level: 14, agent: 'webserver-01', location: '/var/log/apache2/access.log' },
        ];
        
        // Mock agents data
        const mockAgents = [
          { id: '001', name: 'webserver-01', ip: '192.168.1.10', status: 'Active', version: 'v4.7.2', lastKeepAlive: '2026-06-15T14:30:00Z', group: 'webservers' },
          { id: '002', name: 'appserver-02', ip: '192.168.1.11', status: 'Active', version: 'v4.7.2', lastKeepAlive: '2026-06-15T14:29:45Z', group: 'appservers' },
          { id: '003', name: 'dbserver-01', ip: '192.168.1.12', status: 'Active', version: 'v4.7.2', lastKeepAlive: '2026-06-15T14:30:10Z', group: 'dbservers' },
          { id: '004', name: 'firewall-01', ip: '192.168.1.1', status: 'Active', version: 'v4.7.2', lastKeepAlive: '2026-06-15T14:29:55Z', group: 'network' },
        ];
        
        setAlerts(mockAlerts);
        setAgents(mockAgents);
        setLoading(false);
      } catch (err) {
        setError('Failed to load Wazuh SIEM data');
        setLoading(false);
      }
    };

    loadWazuhData();
  }, [timeRange, selectedAgent]);

  useEffect(() => {
    // Check Ollama status
    const checkOllamaStatus = async () => {
      try {
        const response = await fetch('/api/ollama/status');
        if (response.ok) {
          const data = await response.json();
          setOllamaStatus(data.status || 'Connected');
        } else {
          setOllamaStatus('Disconnected');
        }
      } catch (err) {
        setOllamaStatus('Disconnected');
      }
    };

    checkOllamaStatus();
  }, []);

  const analyzeWithAI = async () => {
    if (!prompt.trim()) return;
    
    setIsAnalyzing(true);
    setAiResponse('');
    
    try {
      // Simulate AI analysis
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock AI response based on the prompt and data
      const mockResponse = `Wazuh SIEM Analysis:
      
Based on the current security alerts, I've identified several critical issues:
      
1. High-severity SQL injection attempt on webserver-01 (Level 14)
2. SSH brute force attempts that require immediate attention
3. File integrity changes to system files
      
Recommendations:
- Block the offending IP addresses at the firewall level
- Review and update SQL injection protection rules
- Investigate the file integrity changes to /etc/passwd
- Consider implementing rate limiting for SSH access`;
      
      setAiResponse(mockResponse);
    } catch (err) {
      setAiResponse('Error: Failed to get AI analysis');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getAlertLevelClass = (level: number) => {
    if (level >= 12) return 'critical';
    if (level >= 8) return 'high';
    if (level >= 5) return 'medium';
    return 'low';
  };

  const getAlertLevelText = (level: number) => {
    if (level >= 12) return 'Critical';
    if (level >= 8) return 'High';
    if (level >= 5) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return (
      <div className="tab-content">
        <div className="loading">Loading Wazuh SIEM data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tab-content">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="tab-content">
      <header className="tab-header">
        <h2>Wazuh SIEM</h2>
        <p>Security Information and Event Management</p>
      </header>

      <div className="controls">
        <div className="control-group">
          <label>Wazuh Status: <span className={wazuhStatus === 'Connected' ? 'status-ok' : 'status-error'}>{wazuhStatus}</span></label>
          <label>AI Assistant Status: <span className={ollamaStatus === 'Connected' ? 'status-ok' : 'status-error'}>{ollamaStatus}</span></label>
        </div>
        <div className="control-group">
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="1h">Last 1 hour</option>
            <option value="6h">Last 6 hours</option>
            <option value="12h">Last 12 hours</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
          </select>
          <select value={selectedAgent} onChange={(e) => setSelectedAgent(e.target.value)}>
            <option value="all">All Agents</option>
            {agents.map(agent => (
              <option key={agent.id} value={agent.id}>{agent.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h3>Security Alerts</h3>
          </div>
          <div className="card-content">
            <div className="alerts-list">
              {alerts.map(alert => (
                <div key={alert.id} className={`alert-item ${getAlertLevelClass(alert.level)}`}>
                  <div className="alert-header">
                    <span className="alert-level">{getAlertLevelText(alert.level)} ({alert.level})</span>
                    <span className="alert-time">{new Date(alert.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="alert-body">
                    <h4>{alert.rule}</h4>
                    <p>Agent: {alert.agent} | Location: {alert.location}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Agent Status</h3>
          </div>
          <div className="card-content">
            <div className="agents-list">
              {agents.map(agent => (
                <div key={agent.id} className="agent-item">
                  <div className="agent-header">
                    <h4>{agent.name}</h4>
                    <span className={`agent-status ${agent.status.toLowerCase()}`}>{agent.status}</span>
                  </div>
                  <div className="agent-details">
                    <p>IP: {agent.ip}</p>
                    <p>Group: {agent.group}</p>
                    <p>Last Seen: {new Date(agent.lastKeepAlive).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="ai-section">
        <h3>AI Security Analysis</h3>
        <div className="ai-controls">
          <select 
            value={ollamaModel} 
            onChange={(e) => setOllamaModel(e.target.value)}
            className="model-selector"
          >
            <option value="llama3.2:1b">Llama 3.2 1B</option>
            <option value="llama3.2:3b">Llama 3.2 3B</option>
            <option value="phi3:3.8b">Phi-3 3.8B</option>
          </select>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask AI to analyze security alerts... (e.g., 'What are the most critical threats?')"
            className="prompt-input"
            rows={3}
          />
          <button 
            onClick={analyzeWithAI} 
            disabled={isAnalyzing || !prompt.trim()}
            className="analyze-button"
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}
          </button>
        </div>
        {aiResponse && (
          <div className="ai-response">
            <pre>{aiResponse}</pre>
          </div>
        )}
      </div>
    </div>
  );
}