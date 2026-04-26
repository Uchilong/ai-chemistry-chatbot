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

// Initial table creation (should be done via a migration ideally, but for now we check/create)
export async function initDb() {
  await sql`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;
}
