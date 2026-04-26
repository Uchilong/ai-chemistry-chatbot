import mammoth from 'mammoth';
import { PDFParse } from 'pdf-parse';

export async function parseFile(buffer: Buffer, mimeType: string): Promise<string> {
  if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
    const result = await mammoth.extractRawText({ buffer });
    return result.value;
  }
  
  if (mimeType === 'application/pdf') {
    const parser = new PDFParse({ data: buffer });
    const result = await parser.getText();
    return result.text;
  }

  if (mimeType.startsWith('text/')) {
    return buffer.toString('utf8');
  }

  return '';
}
