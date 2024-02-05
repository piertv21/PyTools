import os
import PyPDF2
import sys

def count_pages_in_folder(folder):
    total_pages = 0

    if not os.path.exists(folder):
        print(f"The folder '{folder}' does not exist.")
        return

    for root, _, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".pdf"):
                file_path = os.path.join(root, filename)

                with open(file_path, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    num_pages = len(pdf_reader.pages)

                    total_pages += num_pages

                    print(f"The file '{filename}' at '{file_path}' contains {num_pages} pages.")

    print(f"\nTotal pages in all PDF files: {total_pages}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/your/folder")
    else:
        folder_to_analyze = sys.argv[1]
        count_pages_in_folder(folder_to_analyze)