import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

const API_URL = 'http://localhost:8000';

const CATEGORIES = [
  { value: 'programming', label: '💻 Programming', color: '#3498db' },
  { value: 'languages', label: '🌍 Languages', color: '#9b59b6' },
  { value: 'fitness', label: '💪 Fitness', color: '#e74c3c' },
  { value: 'music', label: '🎵 Music', color: '#e67e22' },
  { value: 'design', label: '🎨 Design', color: '#1abc9c' },
  { value: 'business', label: '💼 Business', color: '#34495e' },
  { value: 'science', label: '🔬 Science', color: '#16a085' },
  { value: 'personal', label: '🧘 Personal', color: '#f39c12' },
  { value: 'other', label: '📚 Other', color: '#95a5a6' }
];

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [skills, setSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [weakAreas, setWeakAreas] = useState([]);
  const [aiPlan, setAiPlan] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState(null);
  
  // Form states
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillDesc, setNewSkillDesc] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('other');
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskXP, setNewTaskXP] = useState(10);
  
  // Focus Timer states
  const [timerActive, setTimerActive] = useState(false);
  const [timerMinutes, setTimerMinutes] = useState(25);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const timerRef = useRef(null);
  
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const authHeaders = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  // Show notification
  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Fetch functions
  const fetchOverview = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/overview`, { headers: authHeaders });
      if (res.ok) setOverview(await res.json());
    } catch (err) { console.error(err); }
  };

  const fetchUserStats = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/user-stats`, { headers: authHeaders });
      if (res.ok) setUserStats(await res.json());
    } catch (err) { console.error(err); }
  };

  const fetchSkills = async () => {
    try {
      const res = await fetch(`${API_URL}/skills/`, { headers: authHeaders });
      if (res.ok) setSkills(await res.json());
    } catch (err) { console.error(err); }
  };

  const fetchTasks = async (skillId) => {
    try {
      const res = await fetch(`${API_URL}/tasks/${skillId}`, { headers: authHeaders });
      if (res.ok) setTasks(await res.json());
    } catch (err) { console.error(err); }
  };

  const fetchHeatmap = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/activity-heatmap?days=90`, { headers: authHeaders });
      if (res.ok) setHeatmapData(await res.json());
    } catch (err) { console.error(err); }
  };

  const fetchWeakAreas = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/weak-areas`, { headers: authHeaders });
      if (res.ok) setWeakAreas(await res.json());
    } catch (err) { console.error(err); }
  };

  const fetchAIPlan = async () => {
    try {
      const res = await fetch(`${API_URL}/dashboard/ai-recommendation`, { headers: authHeaders });
      if (res.ok) {
        const data = await res.json();
        setAiPlan(data.recommendation || '');
      }
    } catch (err) { console.error(err); }
  };

  // Initial load
  useEffect(() => {
    if (!token) { navigate('/'); return; }
    
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchOverview(),
        fetchUserStats(),
        fetchSkills(),
        fetchHeatmap(),
        fetchWeakAreas(),
        fetchAIPlan()
      ]);
      setLoading(false);
    };
    loadData();
  }, [navigate, token]);

  useEffect(() => {
    if (selectedSkill) fetchTasks(selectedSkill.id);
  }, [selectedSkill]);

  // Focus Timer
  useEffect(() => {
    if (timerActive && (timerMinutes > 0 || timerSeconds > 0)) {
      timerRef.current = setInterval(() => {
        if (timerSeconds === 0) {
          if (timerMinutes === 0) {
            clearInterval(timerRef.current);
            setTimerActive(false);
            showNotification('🎉 Focus session complete! Great work!');
          } else {
            setTimerMinutes(m => m - 1);
            setTimerSeconds(59);
          }
        } else {
          setTimerSeconds(s => s - 1);
        }
      }, 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [timerActive, timerMinutes, timerSeconds]);

  // Handlers
  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;
    
    try {
      const res = await fetch(`${API_URL}/skills/`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          name: newSkillName,
          description: newSkillDesc,
          category: newSkillCategory
        })
      });
      
      if (res.ok) {
        setNewSkillName('');
        setNewSkillDesc('');
        setNewSkillCategory('other');
        await fetchSkills();
        await fetchOverview();
        showNotification('Skill added successfully!');
      }
    } catch (err) { setError(err.message); }
  };

  const handleDeleteSkill = async (skillId) => {
    try {
      const res = await fetch(`${API_URL}/skills/${skillId}`, {
        method: 'DELETE',
        headers: authHeaders
      });
      
      if (res.ok) {
        if (selectedSkill?.id === skillId) {
          setSelectedSkill(null);
          setTasks([]);
        }
        await fetchSkills();
        await fetchOverview();
        showNotification('Skill deleted');
      }
    } catch (err) { setError(err.message); }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim() || !selectedSkill) return;
    
    try {
      const res = await fetch(`${API_URL}/tasks/${selectedSkill.id}`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({ 
          title: newTaskTitle,
          xp_reward: newTaskXP
        })
      });
      
      if (res.ok) {
        setNewTaskTitle('');
        setNewTaskXP(10);
        await fetchTasks(selectedSkill.id);
        await fetchOverview();
        showNotification('Task added!');
      }
    } catch (err) { setError(err.message); }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      const res = await fetch(`${API_URL}/tasks/${taskId}/complete`, {
        method: 'PUT',
        headers: authHeaders
      });
      
      if (res.ok) {
        const data = await res.json();
        await fetchTasks(selectedSkill.id);
        await fetchOverview();
        await fetchUserStats();
        await fetchHeatmap();
        
        if (data.level_up) {
          showNotification(`🎉 LEVEL UP! You're now level ${data.level}!`);
        } else {
          showNotification(`+${data.xp_earned} XP earned! Streak: ${data.current_streak} days 🔥`);
        }
      }
    } catch (err) { setError(err.message); }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const startTimer = (minutes) => {
    setTimerMinutes(minutes);
    setTimerSeconds(0);
    setTimerActive(true);
  };

  const stopTimer = () => {
    setTimerActive(false);
    clearInterval(timerRef.current);
  };

  if (loading) return <div className="dashboard-container">Loading Aptivara...</div>;

  const getCategoryInfo = (cat) => CATEGORIES.find(c => c.value === cat) || CATEGORIES[8];

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      {/* Notification */}
      {notification && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          padding: '1rem 2rem',
          background: notification.type === 'success' ? '#4caf50' : '#f44336',
          color: 'white',
          borderRadius: '8px',
          zIndex: 1000,
          animation: 'slideIn 0.3s ease'
        }}>
          {notification.message}
        </div>
      )}

      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0 }}>🚀 Aptivara</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {userStats && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.9rem' }}>Level {userStats.level} • {userStats.xp_points} XP</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>
                🔥 {userStats.current_streak} day streak
              </div>
            </div>
          )}
          <button onClick={handleLogout} style={{ background: 'rgba(255,255,255,0.2)' }}>
            Logout
          </button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav style={{
        background: 'white',
        padding: '0 2rem',
        borderBottom: '1px solid #ddd',
        display: 'flex',
        gap: '0'
      }}>
        {['overview', 'skills', 'focus', 'analytics', 'ai'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '1rem 1.5rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab ? '3px solid #667eea' : '3px solid transparent',
              color: activeTab === tab ? '#667eea' : '#666',
              fontWeight: activeTab === tab ? 'bold' : 'normal',
              cursor: 'pointer',
              textTransform: 'capitalize'
            }}
          >
            {tab === 'ai' ? '🤖 AI Coach' : tab}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div>
            {/* XP Progress Bar */}
            {userStats && (
              <div style={{
                background: 'white',
                padding: '1.5rem',
                borderRadius: '12px',
                marginBottom: '1.5rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Level {userStats.level}</span>
                  <span>Level {userStats.level + 1}</span>
                </div>
                <div style={{
                  height: '20px',
                  background: '#e0e0e0',
                  borderRadius: '10px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${userStats.level_progress_percent}%`,
                    background: 'linear-gradient(90deg, #667eea, #764ba2)',
                    transition: 'width 0.5s ease'
                  }} />
                </div>
                <div style={{ textAlign: 'center', marginTop: '0.5rem', color: '#666' }}>
                  {userStats.xp_progress_in_level} / {userStats.xp_needed_for_next} XP to next level
                </div>
              </div>
            )}

            {/* Stats Cards */}
            {overview && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                <StatCard value={overview.total_skills} label="Skills" color="#3498db" icon="📚" />
                <StatCard value={overview.total_tasks} label="Total Tasks" color="#e67e22" icon="📝" />
                <StatCard value={overview.completed_tasks} label="Completed" color="#2ecc71" icon="✅" />
                <StatCard value={`${overview.overall_progress_percent}%`} label="Progress" color="#9b59b6" icon="📈" />
              </div>
            )}

            {/* Activity Heatmap */}
            <div style={{
              background: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              marginBottom: '1.5rem',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ margin: '0 0 1rem 0' }}>📅 Activity Heatmap (Last 90 Days)</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px' }}>
                {heatmapData.slice(-90).map((day, idx) => (
                  <div
                    key={idx}
                    title={`${day.date}: ${day.tasks_completed} tasks, ${day.xp_earned} XP`}
                    style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '2px',
                      background: day.intensity === 0 ? '#eee' :
                                  day.intensity === 1 ? '#c6e48b' :
                                  day.intensity === 2 ? '#7bc96f' :
                                  day.intensity === 3 ? '#239a3b' : '#196127'
                    }}
                  />
                ))}
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', fontSize: '0.8rem', color: '#666' }}>
                <span>Less</span>
                {[0, 1, 2, 3, 4].map(i => (
                  <div key={i} style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '2px',
                    background: i === 0 ? '#eee' : i === 1 ? '#c6e48b' : i === 2 ? '#7bc96f' : i === 3 ? '#239a3b' : '#196127'
                  }} />
                ))}
                <span>More</span>
              </div>
            </div>

            {/* Weak Areas */}
            {weakAreas.length > 0 && (
              <div style={{
                background: 'white',
                padding: '1.5rem',
                borderRadius: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ margin: '0 0 1rem 0' }}>⚠️ Areas Needing Attention</h3>
                {weakAreas.map(area => (
                  <div key={area.skill_id} style={{
                    padding: '1rem',
                    background: '#fff3cd',
                    borderRadius: '8px',
                    marginBottom: '0.5rem'
                  }}>
                    <strong>{area.skill_name}</strong> - {area.progress_percent}% complete
                    <div style={{ fontSize: '0.9rem', color: '#666' }}>{area.recommendation}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* SKILLS TAB */}
        {activeTab === 'skills' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Skills Section */}
            <div style={{
              background: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3>My Skills</h3>
              
              <form onSubmit={handleAddSkill} style={{ marginBottom: '1rem' }}>
                <input
                  type="text"
                  placeholder="Skill name"
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                  required
                />
                <input
                  type="text"
                  placeholder="Description"
                  value={newSkillDesc}
                  onChange={(e) => setNewSkillDesc(e.target.value)}
                />
                <select
                  value={newSkillCategory}
                  onChange={(e) => setNewSkillCategory(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem' }}
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
                <button type="submit">Add Skill</button>
              </form>

              {skills.length === 0 ? (
                <p>No skills yet. Add your first skill!</p>
              ) : (
                <div>
                  {skills.map((skill) => {
                    const catInfo = getCategoryInfo(skill.category);
                    return (
                      <div
                        key={skill.id}
                        onClick={() => setSelectedSkill(skill)}
                        style={{
                          padding: '1rem',
                          margin: '0.5rem 0',
                          background: selectedSkill?.id === skill.id ? catInfo.color : '#f5f5f5',
                          color: selectedSkill?.id === skill.id ? 'white' : '#333',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          borderLeft: `4px solid ${catInfo.color}`
                        }}
                      >
                        <div>
                          <strong>{skill.name}</strong>
                          <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>{catInfo.label}</div>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDeleteSkill(skill.id); }}
                          style={{ 
                            background: '#f44336', 
                            padding: '0.25rem 0.5rem', 
                            fontSize: '0.8rem' 
                          }}
                        >
                          ✕
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Tasks Section */}
            <div style={{
              background: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3>Tasks {selectedSkill && `for "${selectedSkill.name}"`}</h3>
              
              {selectedSkill ? (
                <>
                  <form onSubmit={handleAddTask} style={{ marginBottom: '1rem' }}>
                    <input
                      type="text"
                      placeholder="Task title"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      required
                    />
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <label>XP Reward:</label>
                      <input
                        type="number"
                        value={newTaskXP}
                        onChange={(e) => setNewTaskXP(parseInt(e.target.value))}
                        min="5"
                        max="100"
                        style={{ width: '80px' }}
                      />
                    </div>
                    <button type="submit">Add Task</button>
                  </form>

                  {tasks.length === 0 ? (
                    <p>No tasks yet. Add your first task!</p>
                  ) : (
                    <div>
                      {tasks.map((task) => (
                        <div
                          key={task.id}
                          style={{
                            padding: '1rem',
                            margin: '0.5rem 0',
                            background: task.is_completed ? '#e8f5e9' : '#fff',
                            borderRadius: '8px',
                            border: '1px solid #ddd',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                          }}
                        >
                          <div>
                            <span style={{ 
                              textDecoration: task.is_completed ? 'line-through' : 'none' 
                            }}>
                              {task.title}
                            </span>
                            <div style={{ fontSize: '0.8rem', color: '#666' }}>
                              +{task.xp_reward || 10} XP
                            </div>
                          </div>
                          {!task.is_completed && (
                            <button
                              onClick={() => handleCompleteTask(task.id)}
                              style={{ 
                                background: '#4caf50', 
                                padding: '0.5rem 1rem' 
                              }}
                            >
                              Complete ✓
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <p style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                  ← Select a skill to view/add tasks
                </p>
              )}
            </div>
          </div>
        )}

        {/* FOCUS TAB */}
        {activeTab === 'focus' && (
          <div style={{
            background: 'white',
            padding: '3rem',
            borderRadius: '12px',
            textAlign: 'center',
            maxWidth: '500px',
            margin: '0 auto',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h2>🎯 Focus Timer</h2>
            <p style={{ color: '#666' }}>Stay focused and productive!</p>
            
            <div style={{
              fontSize: '5rem',
              fontWeight: 'bold',
              margin: '2rem 0',
              fontFamily: 'monospace',
              color: timerActive ? '#667eea' : '#333'
            }}>
              {String(timerMinutes).padStart(2, '0')}:{String(timerSeconds).padStart(2, '0')}
            </div>

            {!timerActive ? (
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <button onClick={() => startTimer(25)} style={{ background: '#667eea' }}>
                  25 min
                </button>
                <button onClick={() => startTimer(45)} style={{ background: '#764ba2' }}>
                  45 min
                </button>
                <button onClick={() => startTimer(60)} style={{ background: '#e74c3c' }}>
                  60 min
                </button>
              </div>
            ) : (
              <button onClick={stopTimer} style={{ background: '#e74c3c' }}>
                Stop Timer
              </button>
            )}

            <p style={{ marginTop: '2rem', color: '#666', fontSize: '0.9rem' }}>
              💡 Tip: Use the Pomodoro technique - 25 minutes of focused work followed by a 5-minute break.
            </p>
          </div>
        )}

        {/* ANALYTICS TAB */}
        {activeTab === 'analytics' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
              <StatCard value={userStats?.longest_streak || 0} label="Longest Streak" color="#e74c3c" icon="🔥" />
              <StatCard value={userStats?.level || 1} label="Current Level" color="#9b59b6" icon="⭐" />
              <StatCard value={userStats?.xp_points || 0} label="Total XP" color="#f39c12" icon="✨" />
            </div>

            <div style={{
              background: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3>Skills by Category</h3>
              {CATEGORIES.map(cat => {
                const catSkills = skills.filter(s => s.category === cat.value);
                if (catSkills.length === 0) return null;
                return (
                  <div key={cat.value} style={{ marginBottom: '1rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        background: cat.color
                      }} />
                      <strong>{cat.label}</strong>
                      <span style={{ color: '#666' }}>({catSkills.length})</span>
                    </div>
                    <div style={{ paddingLeft: '1.5rem' }}>
                      {catSkills.map(s => (
                        <span key={s.id} style={{
                          display: 'inline-block',
                          padding: '0.25rem 0.75rem',
                          background: '#f0f0f0',
                          borderRadius: '16px',
                          marginRight: '0.5rem',
                          marginBottom: '0.5rem',
                          fontSize: '0.9rem'
                        }}>
                          {s.name}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* AI TAB */}
        {activeTab === 'ai' && (
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h2>🤖 AI Learning Coach</h2>
            <p style={{ color: '#666', marginBottom: '1.5rem' }}>
              Personalized recommendations based on your learning progress
            </p>
            
            <div style={{
              background: 'linear-gradient(135deg, #667eea22 0%, #764ba222 100%)',
              padding: '1.5rem',
              borderRadius: '8px',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6'
            }}>
              {aiPlan || 'Add some skills and complete tasks to get personalized AI recommendations!'}
            </div>

            <button 
              onClick={fetchAIPlan}
              style={{ marginTop: '1rem', background: '#667eea' }}
            >
              🔄 Refresh Recommendations
            </button>

            {weakAreas.length > 0 && (
              <div style={{ marginTop: '2rem' }}>
                <h3>📊 Focus Areas</h3>
                {weakAreas.map(area => (
                  <div key={area.skill_id} style={{
                    padding: '1rem',
                    background: '#fff3cd',
                    borderRadius: '8px',
                    marginBottom: '0.5rem',
                    borderLeft: '4px solid #ffc107'
                  }}>
                    <strong>{area.skill_name}</strong>
                    <div style={{ 
                      marginTop: '0.5rem',
                      height: '8px',
                      background: '#eee',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        height: '100%',
                        width: `${area.progress_percent}%`,
                        background: area.progress_percent < 25 ? '#e74c3c' : '#ffc107'
                      }} />
                    </div>
                    <div style={{ fontSize: '0.8rem', marginTop: '0.25rem', color: '#666' }}>
                      {area.progress_percent}% complete • {area.pending_tasks} tasks remaining
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  );
}

// Stat Card Component
function StatCard({ value, label, color, icon }) {
  return (
    <div style={{
      background: 'white',
      padding: '1.5rem',
      borderRadius: '12px',
      textAlign: 'center',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      borderTop: `4px solid ${color}`
    }}>
      <div style={{ fontSize: '2rem' }}>{icon}</div>
      <div style={{ fontSize: '2rem', fontWeight: 'bold', color }}>{value}</div>
      <div style={{ color: '#666' }}>{label}</div>
    </div>
  );
}

export default Dashboard;