import SummaryCard from './SummaryCard'
import MapCard from './MapCard'
import AnalyticsCard from './AnalyticsCard'
import StatsRow from './StatsRow'
import TimelineSelector from './TimelineSelector'
import VideoList from './VideoList'
import './Dashboard.css'

const Dashboard = ({
  data,
  videos,
  loading,
  videosLoading,
  error,
  videosError,
  selectedDays,
  onTimelineChange,
  onRefreshVideos
}) => {
  if (loading) {
    return (
      <main className="main-content">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i> Loading dashboard data...
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="main-content">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i> Error loading data: {error}
          <br />
          <small>Make sure the backend API is running on http://localhost:5000</small>
        </div>
      </main>
    )
  }

  if (!data) {
    return (
      <main className="main-content">
        <div className="error-message">
          <i className="fas fa-exclamation-circle"></i> No data available
        </div>
      </main>
    )
  }

  const dashboardData = data

  return (
    <main className="main-content">
      {/* Timeline Selector */}
      <TimelineSelector
        selectedDays={selectedDays}
        onTimelineChange={onTimelineChange}
      />

      {/* Dashboard Header */}
      <header className="dashboard-header">
        <div className="header-section">
          <h2 className="section-title">Overview of Public Sentiment</h2>
        </div>
        <div className="header-section">
          <h2 className="section-title">Public Sentiment by Constituents</h2>
        </div>
        <div className="header-section">
          <h2 className="section-title">News and Social Media</h2>
        </div>
      </header>

      {/* Dashboard Grid */}
      <div className="dashboard-grid">
        <SummaryCard
          sentiment={dashboardData.sentiment}
          summary={dashboardData.summary}
          keyIssues={dashboardData.keyIssues}
        />
        <MapCard regions={dashboardData.mapRegions} />
        <AnalyticsCard analytics={dashboardData.analytics} />
      </div>

      {/* Stats Row */}
      <StatsRow stats={dashboardData.stats} />

      {/* Video List Section */}
      <div className="video-section">
        <VideoList
          videos={videos}
          loading={videosLoading}
          error={videosError}
          onRefresh={onRefreshVideos}
        />
      </div>
    </main>
  )
}

export default Dashboard
