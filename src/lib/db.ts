import { neon } from '@neondatabase/serverless';
import bcrypt from 'bcryptjs';

const dbUrl = process.env.DATABASE_URL;
const sql = neon(dbUrl || "postgresql://placeholder:placeholder@localhost:5432/placeholder");

export interface User {
  id: number;
  name: string;
  email: string;
  password: string;
  created_at: string;
}

export interface Chat {
  id: number;
  user_id: number;
  title: string;
  file_data?: string;
  file_name?: string;
  mime_type?: string;
  created_at: string;
}

export interface MessageRecord {
  id: number;
  chat_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export async function createUser(name: string, email: string, password: string): Promise<User> {
  const hashedPassword = bcrypt.hashSync(password, 12);
  const result = await sql`
    INSERT INTO users (name, email, password)
    VALUES (${name}, ${email.toLowerCase()}, ${hashedPassword})
    RETURNING id, name, email, created_at
  `;
  return result[0] as User;
}

export async function getUserByEmail(email: string): Promise<User | undefined> {
  const result = await sql`
    SELECT * FROM users WHERE email = ${email.toLowerCase()}
  `;
  return result[0] as User | undefined;
}

export async function getUserById(id: number): Promise<User | undefined> {
  const result = await sql`
    SELECT * FROM users WHERE id = ${id}
  `;
  return result[0] as User | undefined;
}

export function verifyPassword(plainPassword: string, hashedPassword: string): boolean {
  return bcrypt.compareSync(plainPassword, hashedPassword);
}

// Chat functions
export async function createChat(userId: number, title: string, fileInfo?: { data: string, name: string, type: string }): Promise<Chat> {
  const result = await sql`
    INSERT INTO chats (user_id, title, file_data, file_name, mime_type)
    VALUES (${userId}, ${title}, ${fileInfo?.data || null}, ${fileInfo?.name || null}, ${fileInfo?.type || null})
    RETURNING id, user_id, title, file_data, file_name, mime_type, created_at
  `;
  return result[0] as Chat;
}

export async function getChatById(id: number): Promise<Chat | null> {
  const result = await sql`SELECT * FROM chats WHERE id = ${id}`;
  return (result[0] as Chat) || null;
}

export async function updateChatFile(id: number, fileInfo: { data: string, name: string, type: string }) {
  await sql`
    UPDATE chats 
    SET file_data = ${fileInfo.data}, file_name = ${fileInfo.name}, mime_type = ${fileInfo.type}
    WHERE id = ${id}
  `;
}

export async function addMessage(chatId: number, role: 'user' | 'assistant', content: string): Promise<MessageRecord> {
  const result = await sql`
    INSERT INTO messages (chat_id, role, content)
    VALUES (${chatId}, ${role}, ${content})
    RETURNING id, chat_id, role, content, created_at
  `;
  return result[0] as MessageRecord;
}

export async function getChatsByUserId(userId: number): Promise<Chat[]> {
  const result = await sql`
    SELECT * FROM chats WHERE user_id = ${userId} ORDER BY created_at DESC
  `;
  return result as Chat[];
}

export async function getMessagesByChatId(chatId: number): Promise<MessageRecord[]> {
  const result = await sql`
    SELECT * FROM messages WHERE chat_id = ${chatId} ORDER BY created_at ASC
  `;
  return result as MessageRecord[];
}

export async function deleteChat(chatId: number, userId: number) {
  await sql`DELETE FROM messages WHERE chat_id = ${chatId}`;
  await sql`DELETE FROM chats WHERE id = ${chatId} AND user_id = ${userId}`;
}

// Initial table creation and migrations
export async function initDb() {
  // 1. Create basic tables
  await sql`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS chats (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id),
      title TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS messages (
      id SERIAL PRIMARY KEY,
      chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;

  // 2. Migrations: Add file columns to chats if they don't exist
  try {
    await sql`ALTER TABLE chats ADD COLUMN IF NOT EXISTS file_data TEXT`;
    await sql`ALTER TABLE chats ADD COLUMN IF NOT EXISTS file_name TEXT`;
    await sql`ALTER TABLE chats ADD COLUMN IF NOT EXISTS mime_type TEXT`;
    console.log("Database migrations completed successfully.");
  } catch (e) {
    console.error("Migration error:", e);
  }
}
