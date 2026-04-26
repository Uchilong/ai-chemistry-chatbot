import { getModel } from "@/lib/gemini";
import { NextResponse } from "next/server";
import { Buffer } from "node:buffer";
import { parseFile } from "@/lib/file_parser";
import { addMessage, createChat, getChatById, updateChatFile } from "@/lib/db";

export async function POST(req: Request) {
  console.log("Chat API: Request received");
  try {
    const body = await req.json();
    console.log("Chat API: Body parsed", { model: body.model, hasFile: !!body.fileData });

    const { message, history, model: modelName, fileData, fileName, mimeType, chatId, userId } = body;

    let activeChatId = chatId;
    let effectiveFileData = fileData;
    let effectiveFileName = fileName;
    let effectiveMimeType = mimeType;

    // Đảm bảo userId là kiểu số
    const numericUserId = userId ? Number(userId) : null;

    // Nếu có file mới, xử lý thông tin file
    const newFileInfo = fileData ? {
      data: fileData.split(',')[1],
      name: fileName,
      type: mimeType
    } : null;

    // 1. Nếu là chat mới và có file -> Tạo chat và lưu file
    if (numericUserId && !activeChatId && message) {
      const newChat = await createChat(numericUserId, message.substring(0, 50) || "Cuộc trò chuyện mới", newFileInfo || undefined);
      activeChatId = newChat.id;
    } 
    // 2. Nếu là chat cũ và có file mới -> Cập nhật file cho chat đó
    else if (activeChatId && newFileInfo) {
      await updateChatFile(Number(activeChatId), newFileInfo);
    }
    // 3. Nếu là chat cũ và KHÔNG gửi kèm file -> Lấy file cũ từ DB để làm ngữ cảnh
    else if (activeChatId && !fileData) {
      const chat = await getChatById(Number(activeChatId));
      if (chat?.file_data) {
        effectiveFileData = `data:${chat.mime_type};base64,${chat.file_data}`;
        effectiveFileName = chat.file_name;
        effectiveMimeType = chat.mime_type;
        console.log("Chat API: Using persisted file context from DB", { fileName: effectiveFileName });
      }
    }

    // Save user message
    if (activeChatId) {
      await addMessage(Number(activeChatId), 'user', message || "[Tệp tin]");
    }

    if (!process.env.GEMINI_API_KEY) {
      console.error("Chat API: GEMINI_API_KEY is missing!");
      return NextResponse.json({ error: "API Key is not configured on server" }, { status: 500 });
    }

    const model = getModel(modelName || "gemini-3.1-flash-lite-preview");
    let promptParts: any[] = [{ text: message || "Hãy phân tích tệp này." }];

    if (effectiveFileData) {
      const base64Data = effectiveFileData.split(',')[1];
      const buffer = Buffer.from(base64Data, 'base64');

      if (effectiveMimeType?.startsWith('image/')) {
        promptParts.push({ inlineData: { data: base64Data, mimeType: effectiveMimeType } });
      } else if (effectiveMimeType === 'application/pdf') {
        promptParts.push({ inlineData: { data: base64Data, mimeType: 'application/pdf' } });
      } else {
        try {
          const extractedText = await parseFile(buffer, effectiveMimeType || "");
          if (extractedText) {
            promptParts[0].text = `Nội dung từ tệp "${effectiveFileName}":\n\n${extractedText}\n\n---\n\nCâu hỏi: ${message}`;
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
