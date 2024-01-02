import PyPDF2
import subprocess
import docx2txt


def pdf_extraction(full_file_path,txt_file_path):
    try:
        with open(full_file_path, "rb") as to_be_extracted, open(txt_file_path,"a") as txt_file:

            pdf_reader = PyPDF2.PdfReader(to_be_extracted)
            num_pages = len(pdf_reader.pages)

            text=""

            for page in range(num_pages):
                pdf_page = pdf_reader.pages[page]
                
                page_text = pdf_page.extract_text()
                txt_file.write(page_text)
                text+=page_text+" "

            return text

    except Exception as ex:
        return {"message": "Exception occurred in pdf_extraction","status":"failed"}


def txt_extraction(full_file_path,txt_file_path):
    try:
        with open(full_file_path, "r") as to_be_extracted, open(txt_file_path,"a") as txt_file:
            text = to_be_extracted.read()
            txt_file.write(text)
            return text

    except Exception as ex:
        return {"message": "Exception occurred in txt_extraction","status":"failed"}


def word_docs_extraction(full_file_path,txt_file_path):
    try:
        with open(full_file_path, "r") as to_be_extracted, open(txt_file_path,"a") as txt_file:

            if full_file_path.endswith('.docx'):
                text = docx2txt.process(full_file_path)
                txt_file.write(text)
                return text

                
            elif full_file_path.endswith('.doc'):
                cmd = ['antiword', full_file_path]
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                output = proc.communicate()[0]
                text = output.decode('utf-8')
                txt_file.write(text)
                return text

    except Exception as ex:
        return {"message": "Exception occurred in word_docs_extraction","status":"failed"}
