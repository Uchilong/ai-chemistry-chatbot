import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { getUserByEmail, verifyPassword } from "@/lib/db";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        try {
          const user = await getUserByEmail(credentials.email);
          if (!user) {
            console.log("NextAuth: User not found for email:", credentials.email);
            return null;
          }

          const valid = verifyPassword(credentials.password, user.password);
          if (!valid) {
            console.log("NextAuth: Invalid password for email:", credentials.email);
            return null;
          }

          console.log("NextAuth: Login successful for:", credentials.email);
          return { id: String(user.id), name: user.name, email: user.email };
        } catch (error) {
          console.error("NextAuth authorize error:", error);
          return null;
        }
      }
    })
  ],
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.name = user.name;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id;
        session.user.name = token.name as string;
      }
      return session;
    }
  }
});

export { handler as GET, handler as POST };
