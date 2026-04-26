import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";
import { parseFile } from "@/lib/file-parser";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

export async function POST(req: Request) {
  try {
    const { message, history, model: modelName, fileData, fileName, mimeType } = await req.json();

    const model = genAI.getGenerativeModel({ model: modelName || "gemini-3.1-flash-lite-preview" });

    let promptParts: any[] = [{ text: message }];

    // Handle File Uploads
    if (fileData) {
      const buffer = Buffer.from(fileData.split(',')[1], 'base64');
      
      if (mimeType.startsWith('image/')) {
        promptParts.push({
          inlineData: {
            data: fileData.split(',')[1],
            mimeType: mimeType
          }
        });
      } else {
        const extractedText = await parseFile(buffer, mimeType);
        if (extractedText) {
          promptParts[0].text = `Nội dung từ tệp "${fileName}":\n\n${extractedText}\n\n---\n\nCâu hỏi: ${message}`;
        }
      }
    }

    const chat = model.startChat({
      history: history.map((msg: any) => ({
        role: msg.role === "user" ? "user" : "model",
        parts: [{ text: msg.content }],
      })),
    });

    const result = await chat.sendMessageStream(promptParts);

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        for await (const chunk of result.stream) {
          const chunkText = chunk.text();
          if (chunkText) {
            controller.enqueue(encoder.encode(chunkText));
          }
        }
        controller.close();
      },
    });

    return new Response(stream, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (error) {
    console.error("Chat API Error:", error);
    return NextResponse.json({ error: "Failed to generate response" }, { status: 500 });
  }
}
