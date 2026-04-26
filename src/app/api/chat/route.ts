import { getModel } from "@/lib/gemini";
import { NextResponse } from "next/server";
import { Buffer } from "node:buffer";
import { parseFile } from "@/lib/file_parser";

export async function POST(req: Request) {
  console.log("Chat API: Request received");
  try {
    const body = await req.json();
    console.log("Chat API: Body parsed", { model: body.model, hasFile: !!body.fileData });
    
    const { message, history, model: modelName, fileData, fileName, mimeType } = body;

    if (!process.env.GEMINI_API_KEY) {
      console.error("Chat API: GEMINI_API_KEY is missing!");
      return NextResponse.json({ error: "API Key is not configured on server" }, { status: 500 });
    }

    console.log("Chat API: Initializing model...");
    const model = getModel(modelName || "gemini-3.1-flash-lite-preview");
    
    let promptParts: any[] = [{ text: message || "Hãy phân tích tệp này." }];

    if (fileData) {
      console.log("Chat API: Processing file...", { fileName, mimeType });
      const buffer = Buffer.from(fileData.split(',')[1], 'base64');

      if (mimeType?.startsWith('image/')) {
        promptParts.push({
          inlineData: {
            data: fileData.split(',')[1],
            mimeType: mimeType
          }
        });
      } else {
        try {
          console.log("Chat API: Parsing document...");
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
    const stream = new ReadableStream({
      async start(controller) {
        console.log("Chat API: Stream started");
        try {
          for await (const chunk of result.stream) {
            const chunkText = chunk.text();
            if (chunkText) {
              controller.enqueue(encoder.encode(chunkText));
            }
          }
          console.log("Chat API: Stream finished successfully");
          controller.close();
        } catch (streamError) {
          console.error("Chat API: Streaming error:", streamError);
          controller.error(streamError);
        }
      },
    });

    return new Response(stream, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (error) {
    console.error("Chat API Fatal Error:", error);
    return NextResponse.json({ 
      error: "Failed to generate response", 
      details: error instanceof Error ? error.message : String(error) 
    }, { status: 500 });
  }
}
