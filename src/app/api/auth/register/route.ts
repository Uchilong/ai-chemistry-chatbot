import { NextRequest, NextResponse } from 'next/server';
import { createUser, getUserByEmail, initDb } from '@/lib/db';

export async function POST(req: NextRequest) {
  try {
    await initDb();
    const { name, email, password } = await req.json();

    if (!name || !email || !password) {
      return NextResponse.json({ error: 'Vui lòng điền đầy đủ thông tin.' }, { status: 400 });
    }
    if (password.length < 6) {
      return NextResponse.json({ error: 'Mật khẩu phải có ít nhất 6 ký tự.' }, { status: 400 });
    }

    const existing = await getUserByEmail(email);
    if (existing) {
      return NextResponse.json({ error: 'Email này đã được đăng ký.' }, { status: 409 });
    }

    const user = await createUser(name, email, password);
    return NextResponse.json({ success: true, userId: user.id }, { status: 201 });
  } catch (error) {
    console.error('Register error:', error);
    return NextResponse.json({ error: 'Đã xảy ra lỗi, vui lòng thử lại.' }, { status: 500 });
  }
}
