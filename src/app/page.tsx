'use client';

import { motion } from 'framer-motion';
import { Beaker, Book, MessageSquare, Zap, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#050505] overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-primary/10 blur-[120px] rounded-full" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] bg-accent/10 blur-[120px] rounded-full" />
      </div>

      <nav className="relative z-10 flex items-center justify-between p-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            {/* User needs to save the uploaded image as public/logo.png */}
            <img src="/logo.png" alt="MITC Logo" className="h-12 w-12 object-contain bg-white rounded-full p-0.5" />
            <div className="hidden sm:flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">Trường CĐ Công thương Miền trung</span>
              <span className="text-sm font-bold text-white">Khoa Giáo dục phổ thông</span>
            </div>
          </div>
          <div className="w-px h-10 bg-white/10 hidden md:block mx-2"></div>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/20 rounded-lg hidden sm:block">
              <Beaker className="w-5 h-5 text-primary" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">Hóa Học AI</span>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/login" className="text-gray-400 hover:text-white transition-colors">Đăng nhập</Link>
          <Link href="/register" className="bg-white text-black px-5 py-2.5 rounded-full font-medium hover:bg-gray-200 transition-colors">Bắt đầu ngay</Link>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-32">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-block px-4 py-1.5 bg-primary/10 text-primary rounded-full text-sm font-medium border border-primary/20 mb-6">
              AI Chemistry Tutor 2.0
            </span>
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-6xl md:text-8xl font-bold text-white tracking-tighter leading-tight"
          >
            Làm Chủ Hóa Học <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              Với Trí Tuệ Nhân Tạo
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-400 mt-8 max-w-2xl mx-auto"
          >
            Giải đáp mọi câu hỏi hóa học, phân tích tài liệu, và lên kế hoạch học tập cá nhân hóa với trợ lý AI chuyên nghiệp.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/register" className="w-full sm:w-auto px-8 py-4 bg-primary text-white rounded-2xl font-bold text-lg hover:bg-primary-hover transition-all flex items-center justify-center gap-2 group">
              Bắt đầu hành trình
              <ArrowRight className="group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>

        {/* Features Grid */}
        <div className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<Zap className="w-6 h-6 text-yellow-400" />}
            title="Giải bài tập siêu tốc"
            description="Giải đáp các bài tập hóa học phức tạp chỉ trong vài giây với hướng dẫn chi tiết từng bước."
          />
          <FeatureCard 
            icon={<MessageSquare className="w-6 h-6 text-primary" />}
            title="Hỏi đáp thông minh"
            description="Trò chuyện với AI về mọi chủ đề hóa học, từ cơ bản đến chuyên sâu cấp đại học."
          />
          <FeatureCard 
            icon={<Book className="w-6 h-6 text-accent" />}
            title="Phân tích tài liệu"
            description="Tải lên PDF, Word hoặc hình ảnh đề thi để AI phân tích và giải đáp ngay lập tức."
          />
        </div>
      </main>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="p-8 glass-card"
    >
      <div className="p-3 bg-white/5 rounded-xl w-fit mb-6">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-white mb-4">{title}</h3>
      <p className="text-gray-400 leading-relaxed">{description}</p>
    </motion.div>
  );
}
