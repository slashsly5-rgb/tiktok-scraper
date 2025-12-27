import React from 'react'
import PropTypes from 'prop-types'
import './VideoCard.css'

/**
 * VideoCard Component
 * Displays individual video with engagement metrics, sentiment, and summary
 */
const VideoCard = ({ video }) => {
  // Format numbers with commas
  const formatNumber = (num) => {
    if (!num) return '0'
    return num.toLocaleString()
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // Get sentiment badge color
  const getSentimentColor = (sentiment) => {
    if (!sentiment) return 'neutral'
    const s = sentiment.toLowerCase()
    if (s === 'positive') return 'positive'
    if (s === 'negative' || s === 'very_negative') return 'negative'
    return 'neutral'
  }

  // Get sentiment label
  const getSentimentLabel = (sentiment) => {
    if (!sentiment) return 'Not Analyzed'
    if (sentiment === 'very_negative') return 'Very Negative'
    return sentiment.charAt(0).toUpperCase() + sentiment.slice(1)
  }

  // Calculate engagement rate
  const calculateEngagementRate = () => {
    const views = video.views_count || 0
    if (views === 0) return '0.0'
    const engagement = (video.likes_count || 0) + (video.comments_count || 0) + (video.shares_count || 0)
    const rate = (engagement / views) * 100
    return rate.toFixed(1)
  }

  return (
    <div className="video-card">
      <div className="video-card-header">
        <div className="video-author">
          <i className="fas fa-user-circle"></i>
          <span className="author-name">@{video.author_username || 'unknown'}</span>
        </div>
        {video.sentiment && (
          <span className={`sentiment-badge sentiment-${getSentimentColor(video.sentiment)}`}>
            {getSentimentLabel(video.sentiment)}
          </span>
        )}
      </div>

      <div className="video-card-body">
        <div className="video-description">
          {video.description || 'No description available'}
        </div>

        {video.hashtags && video.hashtags.length > 0 && (
          <div className="video-hashtags">
            {video.hashtags.slice(0, 5).map((tag, index) => (
              <span key={index} className="hashtag">
                {tag.startsWith('#') ? tag : `#${tag}`}
              </span>
            ))}
          </div>
        )}

        {video.summary && (
          <div className="video-summary">
            <strong>AI Summary:</strong>
            <p>{video.summary}</p>
          </div>
        )}

        {video.key_issues && video.key_issues.length > 0 && (
          <div className="video-issues">
            <strong>Key Issues:</strong>
            <div className="issues-list">
              {video.key_issues.map((issue, index) => (
                <span key={index} className="issue-tag">{issue}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="video-card-footer">
        <div className="video-metrics">
          <div className="metric">
            <i className="fas fa-eye"></i>
            <span className="metric-value">{formatNumber(video.views_count)}</span>
            <span className="metric-label">Views</span>
          </div>
          <div className="metric">
            <i className="fas fa-heart"></i>
            <span className="metric-value">{formatNumber(video.likes_count)}</span>
            <span className="metric-label">Likes</span>
          </div>
          <div className="metric">
            <i className="fas fa-comment"></i>
            <span className="metric-value">{formatNumber(video.comments_count)}</span>
            <span className="metric-label">Comments</span>
          </div>
          <div className="metric">
            <i className="fas fa-share"></i>
            <span className="metric-value">{formatNumber(video.shares_count)}</span>
            <span className="metric-label">Shares</span>
          </div>
        </div>

        <div className="video-meta">
          <div className="engagement-rate">
            <i className="fas fa-chart-line"></i>
            <span>{calculateEngagementRate()}% engagement</span>
          </div>
          <div className="video-date">
            <i className="fas fa-calendar"></i>
            <span>{formatDate(video.scraped_at)}</span>
          </div>
        </div>

        {video.url && (
          <a
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
            className="video-link"
          >
            <i className="fab fa-tiktok"></i>
            View on TikTok
          </a>
        )}
      </div>
    </div>
  )
}

VideoCard.propTypes = {
  video: PropTypes.shape({
    id: PropTypes.string,
    tiktok_id: PropTypes.string,
    url: PropTypes.string,
    author_username: PropTypes.string,
    description: PropTypes.string,
    views_count: PropTypes.number,
    likes_count: PropTypes.number,
    comments_count: PropTypes.number,
    shares_count: PropTypes.number,
    hashtags: PropTypes.arrayOf(PropTypes.string),
    search_keyword: PropTypes.string,
    scraped_at: PropTypes.string,
    sentiment: PropTypes.string,
    sentiment_score: PropTypes.number,
    summary: PropTypes.string,
    key_issues: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
}

export default VideoCard
