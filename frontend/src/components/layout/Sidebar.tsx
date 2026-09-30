import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Play,
  FlaskConical,
  GraduationCap,
  CheckSquare,
  History,
  Settings,
  Cpu
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { path: '/dashboard', label: 'Command Center', icon: LayoutDashboard },
    { path: '/simulation', label: 'Simulation Studio', icon: Play, highlight: true },
    { path: '/scenarios', label: 'Scenario Lab', icon: FlaskConical },
    { path: '/academy', label: 'Hadoop Academy', icon: GraduationCap },
    { path: '/assessments', label: 'Assessments', icon: CheckSquare },
    { path: '/history', label: 'History & Insights', icon: History },
  ];

  return (
    <aside style={{
      width: '240px',
      backgroundColor: '#070a12',
      borderRight: '1px solid #1e2942',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      height: '100vh',
      position: 'sticky',
      top: 0,
      zIndex: 40,
      flexShrink: 0
    }}>
      {/* Brand Header */}
      <div>
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #1e2942',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #00f0ff 0%, #0284c7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px rgba(0, 240, 255, 0.4)'
          }}>
            <Cpu size={22} color="#070a12" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{
              fontSize: '18px',
              fontWeight: 800,
              letterSpacing: '1px',
              color: '#ffffff',
              fontFamily: "'JetBrains Mono', monospace"
            }}>
              TEDDY
            </div>
            <div style={{ fontSize: '10px', color: '#00f0ff', letterSpacing: '0.5px' }}>
              HADOOP INTELLIGENCE
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: isActive ? 700 : 500,
                  textDecoration: 'none',
                  color: isActive ? '#00f0ff' : '#94a3b8',
                  backgroundColor: isActive ? 'rgba(0, 240, 255, 0.12)' : 'transparent',
                  border: isActive ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid transparent',
                  boxShadow: isActive ? '0 0 15px rgba(0, 240, 255, 0.2)' : 'none',
                  transition: 'all 0.18s cubic-bezier(0.16, 1, 0.3, 1)'
                })}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.highlight && (
                  <span style={{
                    marginLeft: 'auto',
                    fontSize: '9px',
                    backgroundColor: '#00f0ff',
                    color: '#070a12',
                    fontWeight: 800,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    boxShadow: '0 0 8px rgba(0, 240, 255, 0.5)',
                    fontFamily: "'JetBrains Mono', monospace"
                  }}>
                    HERO
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom Settings Link */}
      <div style={{ padding: '16px 12px', borderTop: '1px solid #1e2942' }}>
        <NavLink
          to="/settings"
          style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: isActive ? 600 : 500,
            textDecoration: 'none',
            color: isActive ? '#00f0ff' : '#94a3b8',
            backgroundColor: isActive ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
            border: isActive ? '1px solid rgba(0, 240, 255, 0.3)' : '1px solid transparent'
          })}
        >
          <Settings size={18} />
          <span>Settings</span>
        </NavLink>
      </div>
    </aside>
  );
};
