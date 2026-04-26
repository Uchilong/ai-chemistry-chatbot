'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';
import { 
  Send, 
  Paperclip, 
  Plus, 
  Settings, 
  User, 
  LogOut, 
  Beaker, 
  Sparkles,
  Bot,
  BrainCircuit,
  MessageSquare,
  Zap,
  Trash2,
  Menu,
  X
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  file?: {
    name: string;
    type: string;
    size: number;
  };
}

export default function ChatPage() {
  const { data: session } = useSession();
  const userName = session?.user?.name || 'Người dùng';
  const userId = (session?.user as any)?.id;
  const userInitial = userName.charAt(0).toUpperCase();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [selectedModel, setSelectedModel] = useState('Gemini AI');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [chats, setChats] = useState<any[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch chat history
  const fetchChats = async () => {
    if (!userId) return;
    try {
      const res = await fetch('/api/chats');
      const data = await res.json();
      if (Array.isArray(data)) setChats(data);
    } catch (err) {
      console.error("Fetch chats error:", err);
    }
  };

  useEffect(() => {
    fetchChats();
  }, [userId]);

  const loadChat = async (id: string) => {
    setIsLoading(true);
    setCurrentChatId(id);
    try {
      const res = await fetch(`/api/chats/${id}`);
      const data = await res.json();
      if (Array.isArray(data)) {
        setMessages(data.map((m: any) => ({
          id: m.id.toString(),
          role: m.role,
          content: m.content
        })));
      }
    } catch (err) {
      console.error("Load chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteChat = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!confirm("Bạn có chắc muốn xóa cuộc trò chuyện này?")) return;
    try {
      await fetch(`/api/chats/${id}`, { method: 'DELETE' });
      setChats(prev => prev.filter(c => c.id.toString() !== id));
      if (currentChatId === id) handleNewChat();
    } catch (err) {
      console.error("Delete chat error:", err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const toBase64 = (file: File) => new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
  });

  const handleNewChat = () => {
    setMessages([]);
    setSelectedFile(null);
    setInput('');
    setCurrentChatId(null);
  };

  const handleSend = async () => {
    if (!input.trim() && !selectedFile || isLoading) return;

    let fileData = '';
    let fileInfo = undefined;
    
    if (selectedFile) {
      fileData = await toBase64(selectedFile);
      fileInfo = {
        name: selectedFile.name,
        type: selectedFile.type,
        size: selectedFile.size
      };
    }

    const userMessage: Message = { 
      id: Date.now().toString(), 
      role: 'user', 
      content: input,
      file: fileInfo
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    const currentFile = selectedFile;
    setSelectedFile(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input || "Hãy phân tích tệp này.",
          history: messages.map(m => ({ role: m.role, content: m.content })),
          model: selectedModel === 'Gemini AI' ? 'gemini-3.1-flash-lite-preview' : 'gemini-pro-latest',
          fileData,
          fileName: currentFile?.name,
          mimeType: currentFile?.type,
          chatId: currentChatId,
          userId: userId
        })
      });

      const serverChatId = response.headers.get("x-chat-id");
      if (serverChatId && !currentChatId) {
        setCurrentChatId(serverChatId);
        fetchChats(); // Refresh sidebar
      }

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = '';
      
      const assistantId = (Date.now() + 1).toString();
      setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        assistantContent += chunk;
        
        setMessages(prev => prev.map(m => 
          m.id === assistantId ? { ...m, content: assistantContent } : m
        ));
      }
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].kind === 'file') {
        const file = items[i].getAsFile();
        if (file) {
          setSelectedFile(file);
          break;
        }
      }
    }
  };

  return (
    <div className="flex h-screen bg-[#050505] text-[#e5e5e5] font-sans selection:bg-primary/30">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="w-72 border-r border-white/5 bg-[#0a0a0a] flex flex-col z-20 shadow-2xl"
          >
            <div className="p-5 border-b border-white/5 flex items-center justify-between">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="p-2 bg-primary/20 rounded-xl group-hover:bg-primary/30 transition-colors">
                  <Beaker className="w-6 h-6 text-primary" />
                </div>
                <span className="font-bold text-lg tracking-tight text-white">Hóa Học AI</span>
              </Link>
              <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden p-2 hover:bg-white/5 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto space-y-4 custom-scrollbar">
              <button className="w-full py-3.5 px-4 rounded-2xl border border-white/10 hover:border-primary/40 hover:bg-white/5 transition-all flex items-center gap-3 text-sm font-medium text-gray-400 hover:text-white group">
                <Plus className="w-4 h-4 group-hover:scale-110 transition-transform" />
                Cuộc trò chuyện mới
              </button>

              <div className="pt-4">
                <h3 className="text-[11px] font-bold text-gray-600 uppercase tracking-[0.2em] px-3 mb-4">Lịch sử</h3>
                <div className="space-y-1">
                  {chats.map((chat) => (
                    <HistoryItem 
                      key={chat.id} 
                      title={chat.title} 
                      active={currentChatId === chat.id.toString()}
                      onClick={() => loadChat(chat.id.toString())}
                      onDelete={(e) => handleDeleteChat(e, chat.id.toString())}
                    />
                  ))}
                  {chats.length === 0 && (
                    <p className="text-[10px] text-gray-600 px-4">Chưa có lịch sử</p>
                  )}
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-white/5">
              <div className="flex items-center gap-3 p-3 rounded-2xl hover:bg-white/5 cursor-pointer transition-all border border-transparent hover:border-white/10">
                <div className="w-10 h-10 bg-gradient-to-tr from-primary to-accent rounded-full flex items-center justify-center font-bold text-white shadow-lg shadow-primary/20">
                  {userInitial}
                </div>
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm font-semibold truncate text-white">{userName}</p>
                  <p className="text-[10px] text-primary font-bold uppercase tracking-wider">Đang hoạt động</p>
                </div>
                <button onClick={() => signOut({ callbackUrl: '/login' })} title="Đăng xuất">
                  <LogOut className="w-4 h-4 text-gray-600 hover:text-red-400 transition-colors" />
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-gradient-to-b from-[#050505] to-[#0a0a0a]">
        {/* Top Header */}
        <header className="p-4 border-b border-white/5 flex items-center justify-between bg-[#050505]/60 backdrop-blur-2xl z-10 sticky top-0">
          <div className="flex items-center gap-4">
            {!isSidebarOpen && (
              <button onClick={() => setIsSidebarOpen(true)} className="p-2.5 hover:bg-white/5 rounded-xl border border-white/5 transition-colors">
                <Menu className="w-5 h-5 text-gray-400" />
              </button>
            )}
            <div className="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/10 hover:border-primary/30 transition-all shadow-inner">
              <Sparkles className="w-4 h-4 text-primary animate-pulse" />
              <select 
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-transparent text-sm font-semibold focus:outline-none cursor-pointer text-white/90"
              >
                <option value="Gemini AI">Gemini 3.1 Flash</option>
                <option value="Gemini Pro">Gemini 3.1 Pro</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2.5 hover:bg-white/5 rounded-xl border border-white/5 transition-colors"><Settings className="w-5 h-5 text-gray-500" /></button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-10 custom-scrollbar scroll-smooth max-w-5xl mx-auto w-full">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-20">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="w-24 h-24 bg-primary/10 rounded-[2.5rem] flex items-center justify-center mb-8 relative"
              >
                <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full" />
                <Bot className="w-12 h-12 text-primary relative z-10" />
              </motion.div>
              <h2 className="text-4xl font-bold text-white mb-4 tracking-tight">Hôm nay bạn học gì?</h2>
              <p className="text-gray-500 text-lg max-w-md mx-auto leading-relaxed">
                Tôi là trợ lý AI chuyên về Hóa học. Tôi có thể giúp bạn giải bài tập, cân bằng phương trình và hơn thế nữa.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-12 w-full max-w-2xl px-4">
                <QuickAction icon={<Zap className="w-5 h-5 text-yellow-500" />} text="Cân bằng phương trình" />
                <QuickAction icon={<BrainCircuit className="w-5 h-5 text-blue-500" />} text="Giải thích liên kết" />
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <motion.div 
                key={m.id} 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 md:gap-6 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-lg ${
                  m.role === 'assistant' 
                  ? 'bg-primary/20 text-primary border border-primary/20' 
                  : 'bg-white/10 text-white border border-white/10'
                }`}>
                  {m.role === 'assistant' ? <Beaker className="w-5 h-5" /> : <User className="w-5 h-5" />}
                </div>
                <div className={`max-w-[85%] flex flex-col gap-2 ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {m.file && (
                    <div className="flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm mb-1">
                      <div className="p-2 bg-primary/20 rounded-lg">
                        <Paperclip className="w-4 h-4 text-primary" />
                      </div>
                      <div className="overflow-hidden">
                        <p className="text-xs font-bold text-white truncate max-w-[150px]">{m.file.name}</p>
                        <p className="text-[9px] text-gray-500 uppercase tracking-wider">{(m.file.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                  )}
                  <div className={`px-6 py-4 rounded-[2rem] shadow-sm ${
                    m.role === 'user' 
                    ? 'bg-primary text-white rounded-tr-none' 
                    : 'bg-white/5 text-gray-200 border border-white/10 rounded-tl-none backdrop-blur-sm'
                  }`}>
                    <div className="prose prose-invert max-w-none text-[15px] leading-relaxed markdown-content">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                          p: ({children}: any) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({children}: any) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
                          ol: ({children}: any) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
                          li: ({children}: any) => <li className="mb-1">{children}</li>,
                          code: ({children}: any) => <code className="bg-white/10 px-1 rounded text-sm font-mono">{children}</code>,
                          strong: ({children}: any) => <strong className="font-bold text-white">{children}</strong>,
                          h3: ({children}: any) => <h3 className="font-bold text-white text-base mt-3 mb-1">{children}</h3>,
                          h4: ({children}: any) => <h4 className="font-semibold text-white text-sm mt-2 mb-1">{children}</h4>,
                        }}
                      >
                        {m.content || (m.file ? "Đã gửi tệp đính kèm." : "")}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-8 max-w-5xl mx-auto w-full relative z-10">
          <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#0a0a0a] to-transparent pointer-events-none" />
          
          <div className="relative group">
            <AnimatePresence>
              {selectedFile && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 10 }}
                  className="absolute bottom-full mb-4 left-0 p-3 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between min-w-[200px] backdrop-blur-xl shadow-2xl"
                >
                  <div className="flex items-center gap-3 px-2">
                    <div className="p-2 bg-primary/20 rounded-lg">
                      <Paperclip className="w-4 h-4 text-primary" />
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-xs font-bold text-white truncate max-w-[150px]">{selectedFile.name}</p>
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setSelectedFile(null)}
                    className="p-1.5 hover:bg-white/10 rounded-xl transition-colors ml-4"
                  >
                    <X className="w-4 h-4 text-gray-500 hover:text-white" />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="relative glass-card border-white/10 focus-within:border-primary/50 focus-within:ring-4 focus-within:ring-primary/5 p-2 flex items-end gap-2 transition-all duration-500 bg-white/[0.02]">
              <input 
                type="file"
                ref={fileInputRef}
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="hidden"
              />
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="p-3.5 hover:bg-white/5 rounded-2xl transition-all text-gray-500 hover:text-primary group"
              >
                <Paperclip className="w-6 h-6 group-hover:rotate-12 transition-transform" />
              </button>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onPaste={handlePaste}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Hỏi bất cứ điều gì hoặc dán tệp vào đây..."
                className="flex-1 bg-transparent border-none focus:outline-none py-3.5 px-2 resize-none max-h-60 min-h-[52px] text-[15px] placeholder:text-gray-600 custom-scrollbar"
                rows={1}
              />
              <button 
                onClick={handleSend}
                disabled={isLoading || (!input.trim() && !selectedFile)}
                className="p-3.5 bg-primary text-white rounded-2xl hover:bg-primary-hover disabled:opacity-30 disabled:grayscale transition-all shadow-lg shadow-primary/20 active:scale-95"
              >
                <Send className="w-6 h-6" />
              </button>
            </div>
            <div className="mt-4 flex items-center justify-center gap-6">
              <p className="text-[10px] text-gray-700 font-bold uppercase tracking-[0.2em] flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-800 rounded-full" />
                Hỗ trợ PDF, Word, Ảnh
              </p>
              <p className="text-[10px] text-gray-700 font-bold uppercase tracking-[0.2em] flex items-center gap-2">
                <span className="w-1 h-1 bg-gray-800 rounded-full" />
                Ctrl + V để dán nhanh
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function HistoryItem({ title, active, onClick, onDelete }: { title: string, active?: boolean, onClick: () => void, onDelete: (e: React.MouseEvent) => void }) {
  return (
    <div 
      onClick={onClick}
      className={`flex items-center justify-between group p-3 px-4 rounded-xl cursor-pointer transition-all border ${
        active 
        ? 'bg-primary/10 border-primary/20 text-white' 
        : 'hover:bg-white/5 border-transparent text-gray-400 hover:text-gray-200'
      }`}
    >
      <div className="flex items-center gap-3 overflow-hidden">
        <MessageSquare className={`w-4 h-4 shrink-0 ${active ? 'text-primary' : 'text-gray-600 group-hover:text-primary'}`} />
        <span className="text-sm truncate">{title}</span>
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          onClick={onDelete}
          className="p-1.5 hover:bg-white/10 rounded-lg text-gray-600 hover:text-red-400"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

function QuickAction({ icon, text }: { icon: React.ReactNode, text: string }) {
  return (
    <button className="flex items-center gap-4 p-5 glass-card text-left text-[15px] font-semibold hover:bg-white/10 group active:scale-[0.98]">
      <div className="shrink-0 transition-transform group-hover:scale-110 duration-300">
        {icon}
      </div>
      <span className="text-gray-300 group-hover:text-white transition-colors">{text}</span>
    </button>
  );
}
