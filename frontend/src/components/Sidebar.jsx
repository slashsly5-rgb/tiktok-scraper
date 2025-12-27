import { useState } from 'react'
import './Sidebar.css'
import projectSLogo from '../assets/ProjectS_Logo.png'
import sarawakFlag from '../assets/SarawakFlag.png'

const Sidebar = () => {
  const [activeItem, setActiveItem] = useState('home')

  const navItems = [
    { id: 'home', icon: 'fa-home', label: 'Analytics' },
    { id: 'assistant', icon: 'fa-robot', label: 'Assistant' },
    // { id: 'analytics', icon: 'fa-chart-line', label: 'Analytics' },
    // { id: 'news', icon: 'fa-newspaper', label: 'News' },
    // { id: 'settings', icon: 'fa-cog', label: 'Settings' },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-container">
          <img src={projectSLogo} alt="Project S" className="logo-image project-s-logo" />
          <img src={sarawakFlag} alt="Sarawak" className="logo-image sarawak-flag" />
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(item => (
          <a
            key={item.id}
            href={`#${item.id}`}
            className={`nav-item ${activeItem === item.id ? 'active' : ''}`}
            onClick={() => setActiveItem(item.id)}
          >
            <i className={`fas ${item.icon} nav-icon`}></i>
            <span className="nav-label">{item.label}</span>
          </a>
        ))}
      </nav>

      <div className="sidebar-user">
        <div className="user-avatar">
          <i className="fas fa-user"></i>
        </div>
        <span className="user-version">Ver 1.1</span>
      </div>
    </aside>
  )
}

export default Sidebar
