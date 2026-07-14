import { useState, useEffect } from 'react';
import { blogAPI } from '../../api';

export default function PostCard({ post, onLike, onDelete, onEdit }) {
  const [showComments, setShowComments] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [comments, setComments] = useState([]);

  useEffect(() => {
    if (showComments && comments.length === 0) {
      loadComments();
    }
  }, [showComments]);

  async function loadComments() {
    try {
      const response = await blogAPI.posts.comments(post.id);
      setComments(response.data || []);
    } catch (error) {
      console.error('Error loading comments:', error);
    }
  }

  async function handleLike() {
    if (onLike) {
      const result = await onLike(post.id);
      if (result) {
        post.likes = result.likes;
        post.is_liked = result.status === 'liked';
      }
    }
  }

  async function handleAddComment(e) {
    e.preventDefault();
    if (!commentText.trim()) return;

    try {
      const result = await blogAPI.posts.addComment(post.id, commentText);
      if (result) {
        setComments([...comments, result.data]);
        setCommentText('');
      }
    } catch (error) {
      console.error('Error adding comment:', error);
      alert('Ошибка при добавлении комментария');
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm p-6 hover:shadow-md transition">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {post.author?.avatar_url ? (
            <img
              src={post.author.avatar_url}
              alt={post.author.username}
              className="w-10 h-10 rounded-full object-cover"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold">
              {post.author?.username?.[0]?.toUpperCase() || '?'}
            </div>
          )}
          <div>
            <p className="font-semibold text-gray-900">{post.author?.username || 'Аноним'}</p>
            <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {post.visibility === 'private' && (
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
              <i className="fas fa-lock mr-1"></i>
              Приватный
            </span>
          )}
          {onEdit && (
            <>
              <button
                onClick={() => onEdit(post)}
                className="p-2 text-gray-400 hover:text-primary transition"
                title="Редактировать"
              >
                <i className="fas fa-pen"></i>
              </button>
              <button
                onClick={() => onDelete(post.id)}
                className="p-2 text-gray-400 hover:text-danger transition"
                title="Удалить"
              >
                <i className="fas fa-trash"></i>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <h3 className="text-xl font-bold text-gray-900 mb-2">{post.title}</h3>
        <p className="text-gray-700 whitespace-pre-wrap">{post.content}</p>
      </div>

      {/* Image */}
      {post.image_url && (
        <div className="mb-4">
          <img
            src={post.image_url}
            alt={post.title}
            className="w-full h-64 object-cover rounded-xl"
          />
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleLike}
            className={`flex items-center space-x-2 transition ${
              post.is_liked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
            }`}
          >
            <i className={`fas ${post.is_liked ? 'fa-heart' : 'fa-heart'}`}></i>
            <span className="text-sm font-medium">{post.likes}</span>
          </button>

          <button
            onClick={() => setShowComments(!showComments)}
            className="flex items-center space-x-2 text-gray-500 hover:text-primary transition"
          >
            <i className="fas fa-comment"></i>
            <span className="text-sm font-medium">{post.comments_count || 0}</span>
          </button>
        </div>
      </div>

      {/* Comments */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <h4 className="font-semibold text-gray-900 mb-3">Комментарии</h4>

          {/* Comment list */}
          <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
            {comments.length > 0 ? (
              comments.map((comment) => (
                <div key={comment.id} className="flex items-start space-x-3">
                  {comment.author?.avatar_url ? (
                    <img
                      src={comment.author.avatar_url}
                      alt={comment.author.username}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-sm font-bold">
                      {comment.author?.username?.[0]?.toUpperCase() || '?'}
                    </div>
                  )}
                  <div className="flex-1 bg-gray-50 rounded-xl p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm text-gray-900">
                        {comment.author?.username || 'Аноним'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(comment.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{comment.content}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm text-center py-4">
                Пока нет комментариев
              </p>
            )}
          </div>

          {/* Add comment */}
          <form onSubmit={handleAddComment} className="flex items-center space-x-2">
            <input
              type="text"
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Написать комментарий..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-indigo-700 transition text-sm font-medium"
            >
              <i className="fas fa-paper-plane"></i>
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
