import { getModel } from "@/lib/gemini";
import { NextResponse } from "next/server";
import { Buffer } from "node:buffer";

export async function POST(req: Request) {
  try {
    const { message, history, model: modelName, fileData, fileName, mimeType } = await req.json();

    const model = getModel(modelName || "gemini-3.1-flash-lite-preview");

    let promptParts: any[] = [{ text: message || "Hãy phân tích tệp này." }];

    // Handle File Uploads
    if (fileData) {
      const buffer = Buffer.from(fileData.split(',')[1], 'base64');

      if (mimeType?.startsWith('image/')) {
        // Images: send inline to Gemini vision
        promptParts.push({
          inlineData: {
            data: fileData.split(',')[1],
            mimeType: mimeType
          }
        });
      } else {
        // Documents: try server-side parsing, fall back gracefully
        try {
          const { parseFile } = await import("@/lib/file_parser");
          const extractedText = await parseFile(buffer, mimeType);
          if (extractedText) {
            promptParts[0].text = `Nội dung từ tệp "${fileName}":\n\n${extractedText}\n\n---\n\nCâu hỏi: ${message}`;
          }
        } catch (parseError) {
          console.warn("File parsing failed, using raw message:", parseError);
          // Chat continues with just the text message — no crash
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
