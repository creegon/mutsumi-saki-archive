'use client';

import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:3001/api';

interface Content {
  id: string;
  type: string;
  source: string;
  sourceUrl: string;
  title: string | null;
  authorName: string | null;
  images: string[];
  tags: string[];
  createdAt: string;
}

interface CrawlerTask {
  id: string;
  name: string;
  source: string;
  keywords: string[];
  status: string;
  lastRunAt: string | null;
}

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  
  const [activeTab, setActiveTab] = useState<'content' | 'crawler' | 'add'>('content');
  const [contents, setContents] = useState<Content[]>([]);
  const [crawlerTasks, setCrawlerTasks] = useState<CrawlerTask[]>([]);
  const [stats, setStats] = useState({ total: 0, byType: {}, bySource: {} });
  
  // Add content form
  const [newContent, setNewContent] = useState({
    type: 'IMAGE',
    source: 'MANUAL',
    sourceUrl: '',
    title: '',
    authorName: '',
    images: '',
    textContent: '',
    tags: '',
  });

  // Add crawler form
  const [newCrawler, setNewCrawler] = useState({
    name: '',
    source: 'PIXIV',
    keywords: '',
  });

  useEffect(() => {
    const savedToken = localStorage.getItem('admin_token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchContents();
      fetchCrawlerTasks();
      fetchStats();
    }
  }, [token]);

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error('登录失败');
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem('admin_token', data.access_token);
    } catch (error) {
      setLoginError('用户名或密码错误');
    }
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('admin_token');
  };

  const fetchContents = async () => {
    try {
      const res = await fetch(`${API_URL}/content?limit=100`);
      const data = await res.json();
      setContents(data.items || []);
    } catch (error) {
      console.error('Failed to fetch contents:', error);
    }
  };

  const fetchCrawlerTasks = async () => {
    try {
      const res = await fetch(`${API_URL}/crawler`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setCrawlerTasks(data || []);
      }
    } catch (error) {
      console.error('Failed to fetch crawler tasks:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/content/stats`);
      const data = await res.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const deleteContent = async (id: string) => {
    if (!confirm('确定删除这个内容吗？')) return;
    try {
      await fetch(`${API_URL}/content/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchContents();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const addContent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const body = {
        ...newContent,
        images: newContent.images.split('\n').filter(Boolean),
        tags: newContent.tags.split(',').map(t => t.trim()).filter(Boolean),
      };
      const res = await fetch(`${API_URL}/content`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        alert('添加成功！');
        setNewContent({
          type: 'IMAGE', source: 'MANUAL', sourceUrl: '', title: '',
          authorName: '', images: '', textContent: '', tags: '',
        });
        fetchContents();
        fetchStats();
      } else {
        alert('添加失败');
      }
    } catch (error) {
      console.error('Failed to add content:', error);
      alert('添加失败');
    }
  };

  const addCrawlerTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const body = {
        ...newCrawler,
        keywords: newCrawler.keywords.split(',').map(k => k.trim()).filter(Boolean),
      };
      const res = await fetch(`${API_URL}/crawler`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        alert('爬虫任务创建成功！');
        setNewCrawler({ name: '', source: 'PIXIV', keywords: '' });
        fetchCrawlerTasks();
      }
    } catch (error) {
      console.error('Failed to add crawler task:', error);
    }
  };

  const deleteCrawlerTask = async (id: string) => {
    if (!confirm('确定删除这个爬虫任务吗？')) return;
    try {
      await fetch(`${API_URL}/crawler/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchCrawlerTasks();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  // Login page
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-pink-400 to-purple-500 bg-clip-text text-transparent">
            🌸 睦祥资源站 - 管理后台
          </h1>
          <form onSubmit={login} className="space-y-4">
            <div>
              <label className="block text-sm text-purple-600 mb-1">用户名</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border-2 border-pink-200 rounded-lg focus:border-pink-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-purple-600 mb-1">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border-2 border-pink-200 rounded-lg focus:border-pink-400 focus:outline-none"
              />
            </div>
            {loginError && <p className="text-red-500 text-sm">{loginError}</p>}
            <button type="submit" className="w-full btn-primary py-3">
              登录
            </button>
          </form>
          <p className="text-center text-sm text-purple-300 mt-4">
            <a href="/" className="hover:text-pink-400">← 返回首页</a>
          </p>
        </div>
      </div>
    );
  }

  // Admin dashboard
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-pink-100">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-pink-400 to-purple-500 bg-clip-text text-transparent">
            🌸 管理后台
          </h1>
          <div className="flex items-center gap-4">
            <a href="/" className="text-sm text-purple-500 hover:text-pink-500">← 返回前台</a>
            <button onClick={logout} className="text-sm text-red-400 hover:text-red-500">退出登录</button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-pink-100">
            <p className="text-3xl font-bold text-pink-500">{stats.total}</p>
            <p className="text-sm text-purple-400">总作品数</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-pink-100">
            <p className="text-3xl font-bold text-purple-500">{(stats.byType as any)?.IMAGE || 0}</p>
            <p className="text-sm text-purple-400">插画</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-pink-100">
            <p className="text-3xl font-bold text-blue-500">{(stats.byType as any)?.TEXT || 0}</p>
            <p className="text-sm text-purple-400">小说</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-pink-100">
            <p className="text-3xl font-bold text-green-500">{crawlerTasks.length}</p>
            <p className="text-sm text-purple-400">爬虫任务</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('content')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              activeTab === 'content' ? 'bg-pink-500 text-white' : 'bg-white text-purple-500 hover:bg-pink-50'
            }`}
          >
            📚 内容管理
          </button>
          <button
            onClick={() => setActiveTab('crawler')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              activeTab === 'crawler' ? 'bg-pink-500 text-white' : 'bg-white text-purple-500 hover:bg-pink-50'
            }`}
          >
            🕷️ 爬虫任务
          </button>
          <button
            onClick={() => setActiveTab('add')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              activeTab === 'add' ? 'bg-pink-500 text-white' : 'bg-white text-purple-500 hover:bg-pink-50'
            }`}
          >
            ➕ 添加内容
          </button>
        </div>

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div className="bg-white rounded-xl shadow-sm border border-pink-100 overflow-hidden">
            <table className="w-full">
              <thead className="bg-pink-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm text-purple-600">标题</th>
                  <th className="px-4 py-3 text-left text-sm text-purple-600">类型</th>
                  <th className="px-4 py-3 text-left text-sm text-purple-600">来源</th>
                  <th className="px-4 py-3 text-left text-sm text-purple-600">作者</th>
                  <th className="px-4 py-3 text-left text-sm text-purple-600">操作</th>
                </tr>
              </thead>
              <tbody>
                {contents.map((content) => (
                  <tr key={content.id} className="border-t border-pink-50 hover:bg-pink-25">
                    <td className="px-4 py-3">
                      <a href={content.sourceUrl} target="_blank" className="text-purple-700 hover:text-pink-500">
                        {content.title?.slice(0, 30) || '无标题'}
                      </a>
                    </td>
                    <td className="px-4 py-3">
                      <span className="tag text-xs">{content.type}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="tag text-xs">{content.source}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-purple-500">{content.authorName || '-'}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => deleteContent(content.id)}
                        className="text-red-400 hover:text-red-500 text-sm"
                      >
                        删除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Crawler Tab */}
        {activeTab === 'crawler' && (
          <div className="space-y-6">
            {/* Add new crawler */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-pink-100">
              <h3 className="font-medium text-purple-700 mb-4">创建新爬虫任务</h3>
              <form onSubmit={addCrawlerTask} className="flex gap-4 items-end">
                <div className="flex-1">
                  <label className="block text-sm text-purple-500 mb-1">任务名称</label>
                  <input
                    type="text"
                    value={newCrawler.name}
                    onChange={(e) => setNewCrawler({ ...newCrawler, name: e.target.value })}
                    placeholder="如：睦祥日更"
                    className="w-full px-3 py-2 border border-pink-200 rounded-lg focus:border-pink-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-purple-500 mb-1">来源</label>
                  <select
                    value={newCrawler.source}
                    onChange={(e) => setNewCrawler({ ...newCrawler, source: e.target.value })}
                    className="px-3 py-2 border border-pink-200 rounded-lg focus:border-pink-400 focus:outline-none"
                  >
                    <option value="PIXIV">Pixiv</option>
                    <option value="LOFTER">Lofter</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="block text-sm text-purple-500 mb-1">关键词（逗号分隔）</label>
                  <input
                    type="text"
                    value={newCrawler.keywords}
                    onChange={(e) => setNewCrawler({ ...newCrawler, keywords: e.target.value })}
                    placeholder="睦祥, 祥睦, MutsumiSaki"
                    className="w-full px-3 py-2 border border-pink-200 rounded-lg focus:border-pink-400 focus:outline-none"
                  />
                </div>
                <button type="submit" className="btn-primary">创建</button>
              </form>
            </div>

            {/* Crawler list */}
            <div className="bg-white rounded-xl shadow-sm border border-pink-100 overflow-hidden">
              <table className="w-full">
                <thead className="bg-pink-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm text-purple-600">名称</th>
                    <th className="px-4 py-3 text-left text-sm text-purple-600">来源</th>
                    <th className="px-4 py-3 text-left text-sm text-purple-600">关键词</th>
                    <th className="px-4 py-3 text-left text-sm text-purple-600">状态</th>
                    <th className="px-4 py-3 text-left text-sm text-purple-600">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {crawlerTasks.map((task) => (
                    <tr key={task.id} className="border-t border-pink-50">
                      <td className="px-4 py-3 text-purple-700">{task.name}</td>
                      <td className="px-4 py-3"><span className="tag text-xs">{task.source}</span></td>
                      <td className="px-4 py-3 text-sm text-purple-500">{task.keywords.join(', ')}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          task.status === 'RUNNING' ? 'bg-green-100 text-green-600' :
                          task.status === 'PAUSED' ? 'bg-yellow-100 text-yellow-600' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {task.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => deleteCrawlerTask(task.id)}
                          className="text-red-400 hover:text-red-500 text-sm"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                  {crawlerTasks.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-purple-300">
                        还没有爬虫任务，创建一个吧！
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
              <p className="text-sm text-purple-600">
                💡 提示：爬虫需要手动运行 Python 脚本。在终端执行：
              </p>
              <code className="block mt-2 bg-white p-2 rounded text-sm text-pink-600">
                cd D:\mutsumi-saki-archive\crawler && python main.py
              </code>
            </div>
          </div>
        )}

        {/* Add Content Tab */}
        {activeTab === 'add' && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-pink-100">
            <h3 className="font-medium text-purple-700 mb-4">手动添加内容</h3>
            <form onSubmit={addContent} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-purple-500 mb-1">类型</label>
                  <select
                    value={newContent.type}
                    onChange={(e) => setNewContent({ ...newContent, type: e.target.value })}
                    className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                  >
                    <option value="IMAGE">插画</option>
                    <option value="TEXT">小说</option>
                    <option value="MANGA">漫画</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-purple-500 mb-1">来源</label>
                  <select
                    value={newContent.source}
                    onChange={(e) => setNewContent({ ...newContent, source: e.target.value })}
                    className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                  >
                    <option value="MANUAL">手动添加</option>
                    <option value="PIXIV">Pixiv</option>
                    <option value="LOFTER">Lofter</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm text-purple-500 mb-1">原链接 *</label>
                <input
                  type="url"
                  required
                  value={newContent.sourceUrl}
                  onChange={(e) => setNewContent({ ...newContent, sourceUrl: e.target.value })}
                  className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                  placeholder="https://..."
                />
              </div>
              <div>
                <label className="block text-sm text-purple-500 mb-1">标题</label>
                <input
                  type="text"
                  value={newContent.title}
                  onChange={(e) => setNewContent({ ...newContent, title: e.target.value })}
                  className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm text-purple-500 mb-1">作者</label>
                <input
                  type="text"
                  value={newContent.authorName}
                  onChange={(e) => setNewContent({ ...newContent, authorName: e.target.value })}
                  className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm text-purple-500 mb-1">图片链接（每行一个）</label>
                <textarea
                  value={newContent.images}
                  onChange={(e) => setNewContent({ ...newContent, images: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                  placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
                />
              </div>
              <div>
                <label className="block text-sm text-purple-500 mb-1">标签（逗号分隔）</label>
                <input
                  type="text"
                  value={newContent.tags}
                  onChange={(e) => setNewContent({ ...newContent, tags: e.target.value })}
                  className="w-full px-3 py-2 border border-pink-200 rounded-lg"
                  placeholder="睦祥, 甜, 日常"
                />
              </div>
              <button type="submit" className="btn-primary">
                添加内容
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
