'use client';

import { useState, useEffect, useMemo } from 'react';
import Lightbox from '@/components/Lightbox';

interface Content {
  id: string;
  type: string;
  source: string;
  sourceUrl: string;
  title: string | null;
  authorName: string | null;
  images: string[];
  textContent: string | null;
  tags: string[];
  likes: number;
  favorites: number;
  createdAt: string;
}

export default function Home() {
  const [allContents, setAllContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState({ type: '', source: '' });
  
  // Lightbox state
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxImages, setLightboxImages] = useState<string[]>([]);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  const [lightboxTitle, setLightboxTitle] = useState('');
  const [lightboxSource, setLightboxSource] = useState('');

  // 加载静态数据
  useEffect(() => {
    fetch('/data.json')
      .then(res => res.json())
      .then(data => {
        setAllContents(data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load data:', err);
        setLoading(false);
      });
  }, []);

  // 过滤和搜索
  const contents = useMemo(() => {
    let filtered = allContents;
    
    if (filter.type) {
      filtered = filtered.filter(c => c.type === filter.type);
    }
    if (filter.source) {
      filtered = filtered.filter(c => c.source === filter.source);
    }
    if (search) {
      const s = search.toLowerCase();
      filtered = filtered.filter(c => 
        (c.title?.toLowerCase().includes(s)) ||
        (c.authorName?.toLowerCase().includes(s)) ||
        c.tags.some(t => t.toLowerCase().includes(s))
      );
    }
    
    return filtered;
  }, [allContents, filter, search]);

  // 统计
  const stats = useMemo(() => {
    const byType: Record<string, number> = {};
    const bySource: Record<string, number> = {};
    allContents.forEach(c => {
      byType[c.type] = (byType[c.type] || 0) + 1;
      bySource[c.source] = (bySource[c.source] || 0) + 1;
    });
    return { total: allContents.length, byType, bySource };
  }, [allContents]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const fetchRandom = () => {
    const shuffled = [...allContents].sort(() => Math.random() - 0.5);
    setAllContents(shuffled);
  };

  const openLightbox = (content: Content, imageIndex: number = 0) => {
    setLightboxImages(content.images);
    setLightboxIndex(imageIndex);
    setLightboxTitle(content.title || '作品');
    setLightboxSource(content.source);
    setLightboxOpen(true);
  };

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Download failed:', error);
      window.open(url, '_blank');
    }
  };

  const downloadAllImages = async (content: Content) => {
    if (content.images.length === 0) return;
    
    for (let i = 0; i < content.images.length; i++) {
      const url = content.images[i];
      const ext = url.includes('.png') ? 'png' : url.includes('.gif') ? 'gif' : 'jpg';
      const filename = `${(content.title || 'image').replace(/[<>:"/\\|?*]/g, '_')}_${i + 1}.${ext}`;
      await handleDownload(url, filename);
      if (i < content.images.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  };

  return (
    <div className="min-h-screen">
      {/* Lightbox */}
      {lightboxOpen && (
        <Lightbox
          images={lightboxImages}
          initialIndex={lightboxIndex}
          title={lightboxTitle}
          source={lightboxSource}
          onClose={() => setLightboxOpen(false)}
          onDownload={handleDownload}
        />
      )}

      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-white/70 border-b border-pink-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-400 to-purple-500 bg-clip-text text-transparent">
              🌸 睦祥资源站
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-purple-600">
                共 {stats.total} 个作品
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search & Filters */}
        <div className="mb-8 space-y-4">
          <form onSubmit={handleSearch} className="flex gap-4">
            <input
              type="text"
              placeholder="搜索作品、作者..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-box flex-1"
            />
            <button type="button" onClick={fetchRandom} className="btn-primary bg-gradient-to-r from-purple-400 to-pink-400">
              🎲 随机
            </button>
          </form>

          <div className="flex flex-wrap gap-2">
            {/* Type filters */}
            <button
              onClick={() => setFilter({ ...filter, type: '' })}
              className={`tag ${!filter.type ? 'ring-2 ring-purple-400' : ''}`}
            >
              全部类型
            </button>
            <button
              onClick={() => setFilter({ ...filter, type: 'IMAGE' })}
              className={`tag ${filter.type === 'IMAGE' ? 'ring-2 ring-purple-400' : ''}`}
            >
              🖼️ 插画 ({stats.byType['IMAGE'] || 0})
            </button>
            <button
              onClick={() => setFilter({ ...filter, type: 'TEXT' })}
              className={`tag ${filter.type === 'TEXT' ? 'ring-2 ring-purple-400' : ''}`}
            >
              📝 小说 ({stats.byType['TEXT'] || 0})
            </button>
            <button
              onClick={() => setFilter({ ...filter, type: 'MANGA' })}
              className={`tag ${filter.type === 'MANGA' ? 'ring-2 ring-purple-400' : ''}`}
            >
              📚 漫画 ({stats.byType['MANGA'] || 0})
            </button>

            <span className="mx-2 text-pink-300">|</span>

            {/* Source filters */}
            <button
              onClick={() => setFilter({ ...filter, source: '' })}
              className={`tag ${!filter.source ? 'ring-2 ring-purple-400' : ''}`}
            >
              全部来源
            </button>
            <button
              onClick={() => setFilter({ ...filter, source: 'PIXIV' })}
              className={`tag ${filter.source === 'PIXIV' ? 'ring-2 ring-purple-400' : ''}`}
            >
              Pixiv ({stats.bySource['PIXIV'] || 0})
            </button>
            <button
              onClick={() => setFilter({ ...filter, source: 'TWITTER' })}
              className={`tag ${filter.source === 'TWITTER' ? 'ring-2 ring-purple-400' : ''}`}
            >
              Twitter ({stats.bySource['TWITTER'] || 0})
            </button>
          </div>
        </div>

        {/* Content Grid */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-pink-300 border-t-pink-500"></div>
          </div>
        ) : contents.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🌸</div>
            <p className="text-purple-400 text-lg">没有找到相关内容～</p>
          </div>
        ) : (
          <div className="masonry">
            {contents.slice(0, 100).map((content) => (
              <div key={content.id} className="masonry-item">
                <div className="content-card">
                  {/* Image */}
                  {content.images.length > 0 && (
                    <div className="relative group cursor-pointer" onClick={() => openLightbox(content, 0)}>
                      <img
                        src={content.images[0]}
                        alt={content.title || '作品'}
                        className="w-full object-cover"
                        loading="lazy"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect fill="%23fce7f3" width="400" height="300"/><text fill="%23e879a9" font-size="20" x="50%" y="50%" text-anchor="middle">🌸 图片加载失败</text></svg>';
                        }}
                      />
                      
                      {/* Hover overlay with actions */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            openLightbox(content, 0);
                          }}
                          className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                          title="查看大图"
                        >
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                          </svg>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            downloadAllImages(content);
                          }}
                          className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                          title="下载全部图片"
                        >
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                        </button>
                        <a
                          href={content.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                          title="查看原链接"
                        >
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      </div>

                      {/* Image count badge */}
                      {content.images.length > 1 && (
                        <div className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full">
                          📷 {content.images.length}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Content */}
                  <div className="p-4">
                    <h3 className="font-medium text-purple-800 mb-2 line-clamp-2">
                      <a href={content.sourceUrl} target="_blank" rel="noopener noreferrer" className="hover:text-pink-500">
                        {content.title || '无标题'}
                      </a>
                    </h3>

                    {content.authorName && (
                      <p className="text-sm text-purple-400 mb-2">
                        by {content.authorName}
                      </p>
                    )}

                    {/* Text preview for novels */}
                    {content.type === 'TEXT' && content.textContent && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                        {content.textContent.substring(0, 150)}...
                      </p>
                    )}

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      <span className="tag text-xs">{content.source}</span>
                      <span className="tag text-xs">{content.type === 'IMAGE' ? '插画' : content.type === 'TEXT' ? '小说' : '漫画'}</span>
                      {content.tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="tag text-xs">{tag}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {contents.length > 100 && (
          <div className="text-center py-8 text-purple-400">
            显示前 100 个结果，共 {contents.length} 个
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-8 text-purple-300 text-sm">
        <p>🌸 睦祥资源站 - 若叶睦 × 丰川祥子 🌸</p>
        <p className="mt-1">Made with 💜 for MutsumiSaki fans</p>
      </footer>
    </div>
  );
}
