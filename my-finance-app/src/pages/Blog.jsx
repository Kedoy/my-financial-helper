import { useState, useEffect } from 'react';
import { blogAPI } from '../api';
import PostCard from '../components/blog/PostCard';
import PostModal from '../components/blog/PostModal';

export default function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPost, setEditingPost] = useState(null);
  const [filter, setFilter] = useState('all'); // all, my, public

  useEffect(() => {
    loadPosts();
  }, [filter]);

  async function loadPosts() {
    setLoading(true);
    try {
      const params = {};
      if (filter === 'my') {
        // Загружаем все посты, фильтрация будет на клиенте
        params.limit = 100;
      }
      const response = await blogAPI.posts.list(params);
      let allPosts = response.data.results || response.data || [];

      // Фильтрация на клиенте
      if (filter === 'my') {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        allPosts = allPosts.filter(post => post.author?.id === user.id);
      } else if (filter === 'public') {
        allPosts = allPosts.filter(post => post.visibility === 'public');
      }

      setPosts(allPosts);
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreatePost(data) {
    if (editingPost) {
      await blogAPI.posts.update(editingPost.id, data);
    } else {
      await blogAPI.posts.create(data);
    }
    await loadPosts();
  }

  async function handleDeletePost(id) {
    if (!confirm('Вы уверены, что хотите удалить этот пост?')) return;

    try {
      await blogAPI.posts.delete(id);
      await loadPosts();
    } catch (error) {
      console.error('Error deleting post:', error);
      alert('Ошибка при удалении поста');
    }
  }

  async function handleLike(id) {
    try {
      const post = posts.find(p => p.id === id);
      if (post?.is_liked) {
        const result = await blogAPI.posts.unlike(id);
        return result.data;
      } else {
        const result = await blogAPI.posts.like(id);
        return result.data;
      }
    } catch (error) {
      console.error('Error liking post:', error);
    }
  }

  async function handleEdit(post) {
    setEditingPost(post);
    setShowModal(true);
  }

  function handleCloseModal() {
    setShowModal(false);
    setEditingPost(null);
  }

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Блог</h1>
          <p className="text-gray-600 mt-1">Делитесь знаниями о финансовой грамотности</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-6 py-3 bg-primary text-white rounded-xl hover:bg-indigo-700 transition font-medium shadow-lg shadow-primary/30"
        >
          <i className="fas fa-plus mr-2"></i>
          Создать пост
        </button>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {[
          { value: 'all', label: 'Все посты' },
          { value: 'public', label: 'Публичные' },
          { value: 'my', label: 'Мои посты' },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setFilter(tab.value)}
            className={`px-4 py-2 rounded-xl font-medium transition ${
              filter === tab.value
                ? 'bg-primary text-white shadow-lg shadow-primary/30'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : posts.length > 0 ? (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onLike={handleLike}
              onDelete={post.author?.id === user.id ? handleDeletePost : null}
              onEdit={post.author?.id === user.id ? handleEdit : null}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-gray-500">
          <i className="fas fa-newspaper text-6xl mb-4 text-gray-300"></i>
          <p className="text-lg font-medium">Постов пока нет</p>
          <p className="text-sm mt-1">Будьте первым, кто опубликует пост!</p>
        </div>
      )}

      {/* Create/Edit Modal */}
      <PostModal
        isOpen={showModal}
        onClose={handleCloseModal}
        onSubmit={handleCreatePost}
        editingPost={editingPost}
      />
    </div>
  );
}
