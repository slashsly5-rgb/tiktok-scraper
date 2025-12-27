import './Cards.css'

const SummaryCard = ({ sentiment, summary, keyIssues }) => {
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return '↑'
      case 'down': return '↓'
      default: return '→'
    }
  }

  return (
    <div className="summary-card fade-in">
      <div className={`sentiment-badge ${sentiment.type}`}>
        {sentiment.overall}
      </div>

      <h3 className="card-title">Briefing Summary</h3>

      <p className="card-description">{summary}</p>

      <div className="key-issues">
        <h4 className="issues-title">Key Issues</h4>
        <ul className="issues-list">
          {keyIssues.map((issue, index) => (
            <li key={index} className={`issue-item trending-${issue.trend}`}>
              <span className="issue-icon">{getTrendIcon(issue.trend)}</span>
              <span>{issue.name}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default SummaryCard
