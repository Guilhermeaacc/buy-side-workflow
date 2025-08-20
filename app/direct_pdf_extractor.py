import openai
import os
import base64
import logging
import tempfile
from dotenv import load_dotenv
from PyPDF2 import PdfReader, PdfWriter

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectPDFExtractor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.max_pages_per_chunk = 20
    
    def count_pdf_pages(self, pdf_path: str) -> int:
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            logger.error(f"❌ Error counting PDF pages: {str(e)}")
            raise Exception(f"Failed to count PDF pages: {str(e)}")
    
    def split_pdf_into_chunks(self, pdf_path: str) -> list:
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            chunk_files = []
            
            for chunk_start in range(0, total_pages, self.max_pages_per_chunk):
                chunk_end = min(chunk_start + self.max_pages_per_chunk, total_pages)
                
                writer = PdfWriter()
                for page_num in range(chunk_start, chunk_end):
                    writer.add_page(reader.pages[page_num])
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                with open(temp_file.name, 'wb') as output_pdf:
                    writer.write(output_pdf)
                
                # Verify chunk content
                chunk_file_size = os.path.getsize(temp_file.name)
                
                # Verify the chunk is readable
                try:
                    chunk_reader = PdfReader(temp_file.name)
                    actual_page_count = len(chunk_reader.pages)
                    logger.info(f"✅ Chunk verification: {actual_page_count} pages, {chunk_file_size} bytes")
                except Exception as verify_error:
                    logger.error(f"❌ Chunk verification failed: {verify_error}")
                
                chunk_files.append({
                    'file_path': temp_file.name,
                    'start_page': chunk_start + 1,
                    'end_page': chunk_end,
                    'page_count': chunk_end - chunk_start,
                    'file_size': chunk_file_size
                })
                
                logger.info(f"📄 Created chunk: pages {chunk_start + 1}-{chunk_end} ({chunk_end - chunk_start} pages, {chunk_file_size} bytes)")
            
            return chunk_files
            
        except Exception as e:
            logger.error(f"❌ Error splitting PDF: {str(e)}")
            raise Exception(f"Failed to split PDF: {str(e)}")
    
    async def extract_text_from_single_pdf(self, pdf_path: str, start_page: int = None, end_page: int = None) -> str:
        try:
            # Log detailed chunk information
            if start_page and end_page:
                file_size = os.path.getsize(pdf_path)
                logger.info(f"📄 Processing PDF chunk: {pdf_path} (pages {start_page}-{end_page}, {file_size} bytes)")
            else:
                file_size = os.path.getsize(pdf_path)
                logger.info(f"📄 Processing single PDF: {pdf_path} ({file_size} bytes)")
            
            # 1. Upload PDF via Files API
            with open(pdf_path, "rb") as f:
                upload = self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            
            logger.info(f"✅ PDF uploaded successfully. File ID: {upload.id}, Size: {file_size} bytes")
            
            # 2. Use single unified extraction prompt for all cases
            extraction_prompt = """Extract the text content from this PDF document in strict chronological page order.

Preserve the exact text content as it appears in the PDF

Make sure that you can transcribe the data in a smart way and logic structure

Do not reorder or reorganize the content

Return only the text with clear page markers like:
=
[content of page 1]
=
[content of page 2]"""
            
            # 3. Use Responses API with file_id for actual extraction
            logger.info(f"📝 Sending extraction prompt: {extraction_prompt[:100]}...")
            response = self.client.responses.create(
                model="gpt-4o",
                input=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text", 
                            "text": extraction_prompt
                        },
                        {
                            "type": "input_file", 
                            "file_id": upload.id
                        }
                    ]
                }]
            )
            
            extracted_text = response.output_text
            
            # Check for refusal responses
            if len(extracted_text) < 500 and any(refusal_phrase in extracted_text.lower() for refusal_phrase in [
                "unable to assist", "unable to transcribe", "can't help", "cannot help", 
                "i'm unable", "use ocr", "extract text", "provide the text"
            ]):
                logger.warning(f"⚠️ Possible refusal response detected: {extracted_text}")
                logger.warning(f"⚠️ Response length: {len(extracted_text)} characters")
            
            logger.info(f"✅ PDF text extraction completed. Text length: {len(extracted_text)} characters")
            logger.info(f"📄 Response preview: {extracted_text[:300]}...")
            
            # 3. Clean up the uploaded file
            self.client.files.delete(upload.id)
            logger.info(f"🗑️ Cleaned up uploaded file: {upload.id}")
            
            return extracted_text
                
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {str(e)}")
            # Try to clean up file if it was uploaded
            try:
                if 'upload' in locals():
                    self.client.files.delete(upload.id)
            except:
                pass
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            # Count pages to determine if we need chunking
            total_pages = self.count_pdf_pages(pdf_path)
            logger.info(f"📊 PDF has {total_pages} pages")
            
            # If PDF is small enough, process normally
            if total_pages <= self.max_pages_per_chunk:
                logger.info(f"📄 PDF is small ({total_pages} pages), processing normally")
                return await self.extract_text_from_single_pdf(pdf_path)
            
            # If PDF is large, split into chunks and process each
            logger.info(f"📄 PDF is large ({total_pages} pages), splitting into chunks")
            chunk_files = self.split_pdf_into_chunks(pdf_path)
            
            all_extracted_texts = []
            
            try:
                for i, chunk_info in enumerate(chunk_files):
                    chunk_path = chunk_info['file_path']
                    start_page = chunk_info['start_page']
                    end_page = chunk_info['end_page']
                    
                    logger.info(f"🔄 Processing chunk {i + 1}/{len(chunk_files)}: pages {start_page}-{end_page}")
                    
                    chunk_text = await self.extract_text_from_single_pdf(chunk_path, start_page, end_page)
                    
                    # Add chunk header to ensure proper sequencing
                    chunk_with_header = f"=== CHUNK {i + 1}: PAGES {start_page}-{end_page} ===\n\n{chunk_text}"
                    all_extracted_texts.append(chunk_with_header)
                    
                    logger.info(f"✅ Completed chunk {i + 1}/{len(chunk_files)}")
                
                # Merge all texts in order with clear separators
                final_text = "\n\n" + "="*50 + "\n\n".join(all_extracted_texts) + "\n\n" + "="*50
                
                logger.info(f"✅ All chunks processed. Final text length: {len(final_text)} characters")
                logger.info(f"📄 Final text preview: {final_text[:200]}...")
                
                return final_text
                
            finally:
                # Clean up temporary chunk files
                for chunk_info in chunk_files:
                    try:
                        os.unlink(chunk_info['file_path'])
                        logger.info(f"🗑️ Cleaned up chunk file: {chunk_info['file_path']}")
                    except Exception as cleanup_error:
                        logger.warning(f"⚠️ Failed to clean up chunk file {chunk_info['file_path']}: {cleanup_error}")
                
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")