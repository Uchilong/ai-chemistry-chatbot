import { GoogleGenerativeAI } from "@google/generative-ai";

const apiKey = process.env.GEMINI_API_KEY || "";
const genAI = new GoogleGenerativeAI(apiKey);

export const getModel = (modelName: string = "gemini-2.0-flash") => {
  return genAI.getGenerativeModel({ model: modelName });
};

export const CHAT_CONFIG = {
  temperature: 0.7,
  topP: 0.8,
  topK: 40,
  maxOutputTokens: 2048,
};
