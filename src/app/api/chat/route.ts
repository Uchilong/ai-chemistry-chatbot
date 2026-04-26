import { getModel } from "@/lib/gemini";
import { NextResponse } from "next/server";
import { Buffer } from "node:buffer";
import { parseFile } from "@/lib/file_parser";
import { addMessage, createChat } from "@/lib/db";

export async function POST(req: Request) {
  console.log("Chat API: Request received");
  try {
    const body = await req.json();
    console.log("Chat API: Body parsed", { model: body.model, hasFile: !!body.fileData });

    const { message, history, model: modelName, fileData, fileName, mimeType, chatId, userId } = body;

    let activeChatId = chatId;

    // Đảm bảo userId là kiểu số (NextAuth có thể trả về chuỗi)
    const numericUserId = userId ? Number(userId) : null;

    // If logged in and starting a new chat, create it
    if (numericUserId && !activeChatId && message) {
      const newChat = await createChat(numericUserId, message.substring(0, 50) || "Cuộc trò chuyện mới");
      activeChatId = newChat.id;
    }

    // Save user message if chatId is available
    if (activeChatId) {
      await addMessage(Number(activeChatId), 'user', message || "[Tệp tin]");
    }

    if (!process.env.GEMINI_API_KEY) {
      console.error("Chat API: GEMINI_API_KEY is missing!");
      return NextResponse.json({ error: "API Key is not configured on server" }, { status: 500 });
    }

    console.log("Chat API: Initializing model...");
    const model = getModel(modelName || "gemini-3.1-flash-lite-preview");

    let promptParts: any[] = [{ text: message || "Hãy phân tích tệp này." }];

    if (fileData) {
      console.log("Chat API: Processing file...", { fileName, mimeType });
      const base64Data = fileData.split(',')[1];
      const buffer = Buffer.from(base64Data, 'base64');

      if (mimeType?.startsWith('image/')) {
        promptParts.push({
          inlineData: {
            data: base64Data,
            mimeType: mimeType
          }
        });
      } else if (mimeType === 'application/pdf') {
        // Native PDF support: Gemini will see text AND images
        console.log("Chat API: Sending PDF directly to Gemini (Native Support)");
        promptParts.push({
          inlineData: {
            data: base64Data,
            mimeType: 'application/pdf'
          }
        });
      } else {
        try {
          console.log("Chat API: Parsing document text...");
          const extractedText = await parseFile(buffer, mimeType);
          if (extractedText) {
            promptParts[0].text = `Nội dung từ tệp "${fileName}":\n\n${extractedText}\n\n---\n\nCâu hỏi: ${message}`;
          }
        } catch (parseError) {
          console.warn("File parsing failed:", parseError);
        }
      }
    }

    console.log("Chat API: Starting chat session...");
    const chat = model.startChat({
      history: history.map((msg: any) => ({
        role: msg.role === "user" ? "user" : "model",
        parts: [{ text: msg.content }],
      })),
    });

    console.log("Chat API: Sending message stream...");
    const result = await chat.sendMessageStream(promptParts);

    const encoder = new TextEncoder();
    let assistantContent = "";

    const stream = new ReadableStream({
      async start(controller) {
        console.log("Chat API: Stream started");
        try {
          for await (const chunk of result.stream) {
            const chunkText = chunk.text();
            if (chunkText) {
              assistantContent += chunkText;
              controller.enqueue(encoder.encode(chunkText));
            }
          }
          console.log("Chat API: Stream finished successfully");
          if (activeChatId && assistantContent) {
            await addMessage(Number(activeChatId), 'assistant', assistantContent);
          }
          controller.close();
        } catch (streamError) {
          console.error("Chat API: Streaming error:", streamError);
          controller.error(streamError);
        }
      },
    });

    return new Response(stream, {
      headers: { 
        "Content-Type": "text/plain; charset=utf-8",
        "x-chat-id": String(activeChatId || "")
      },
    });
  } catch (error) {
    console.error("Chat API Fatal Error:", error);
    return NextResponse.json({
      error: "Failed to generate response",
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
