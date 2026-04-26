import { NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { getChatsByUserId, initDb } from "@/lib/db";

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.email) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const userId = (session.user as any).id;
    if (!userId) return NextResponse.json([], { status: 200 });

    // Đảm bảo bảng chats và messages đã được tạo (dành cho user cũ)
    await initDb();

    const chats = await getChatsByUserId(Number(userId));
    return NextResponse.json(chats);
  } catch (error) {
    console.error("Fetch chats error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
