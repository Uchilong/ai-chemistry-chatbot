import mammoth from 'mammoth';
import * as pdf from 'pdf-parse';

export async function parseFile(buffer: Buffer, mimeType: string): Promise<string> {
  if (mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
    const result = await mammoth.extractRawText({ buffer });
    return result.value;
  }

  if (mimeType === 'application/pdf') {
    try {
      const data = await (pdf as any)(buffer);
      return data.text;
    } catch (err) {
      console.error('PDF parsing error:', err);
      return '';
    }
  }

  if (mimeType.startsWith('text/')) {
    return buffer.toString('utf8');
  }

  return '';
}
