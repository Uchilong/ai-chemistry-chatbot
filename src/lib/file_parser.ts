import mammoth from 'mammoth';

// Polyfill for PDF parsing on Vercel/Node environment
if (typeof (global as any).DOMMatrix === 'undefined') {
  (global as any).DOMMatrix = class DOMMatrix {};
}
if (typeof (global as any).ImageData === 'undefined') {
  (global as any).ImageData = class ImageData {};
}
if (typeof (global as any).Path2D === 'undefined') {
  (global as any).Path2D = class Path2D {};
}

export async function parseFile(buffer: Buffer, mimeType: string): Promise<string> {
  if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
    const result = await mammoth.extractRawText({ buffer });
    return result.value;
  }

  if (mimeType === 'application/pdf') {
    try {
      // Dynamic import to prevent crash at startup
      const pdf = (await import('pdf-parse')).default;
      const data = await (pdf as any)(buffer);
      return data.text;
    } catch (err) {
      console.error('PDF parsing error:', err);
      return 'Lỗi khi đọc file PDF.';
    }
  }

  if (mimeType.startsWith('text/')) {
    return buffer.toString('utf8');
  }

  return '';
}
