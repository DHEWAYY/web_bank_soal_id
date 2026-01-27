import json
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. TEMPLATE HTML (Sama kayak kemaren) ---
TEMPLATE_PG = """
<article class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
    <div class="flex gap-3">
        <span class="bg-blue-100 text-blue-700 font-bold px-3 py-1 rounded h-fit text-sm">{NO}.</span>
        <div class="w-full">
            <p class="text-lg font-medium mb-4">{PERTANYAAN}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <button class="text-left px-4 py-2 rounded border hover:bg-blue-50 text-sm"><span class="font-bold mr-2">A.</span> {OPSI_A}</button>
                <button class="text-left px-4 py-2 rounded border hover:bg-blue-50 text-sm"><span class="font-bold mr-2">B.</span> {OPSI_B}</button>
                <button class="text-left px-4 py-2 rounded border hover:bg-blue-50 text-sm"><span class="font-bold mr-2">C.</span> {OPSI_C}</button>
                <button class="text-left px-4 py-2 rounded border hover:bg-blue-50 text-sm"><span class="font-bold mr-2">D.</span> {OPSI_D}</button>
            </div>
            <details class="group">
                <summary class="flex cursor-pointer items-center gap-2 text-blue-600 font-semibold text-sm select-none"><i class="fa-solid fa-key"></i> Lihat Pembahasan</summary>
                <div class="mt-3 bg-gray-50 border-l-4 border-blue-500 p-4 text-sm rounded"><p class="font-bold text-gray-900 mb-1">Jawaban: {JAWABAN}</p><p class="text-gray-700 whitespace-pre-line">{PEMBAHASAN}</p></div>
            </details>
        </div>
    </div>
</article>
"""

TEMPLATE_ESSAY = """
<article class="bg-white p-6 rounded-xl shadow-sm border border-orange-100 mb-6">
    <div class="flex gap-3">
        <span class="bg-orange-100 text-orange-700 font-bold px-3 py-1 rounded h-fit text-sm">Esai {NO}.</span>
        <div class="w-full">
            <p class="text-lg font-medium mb-4">{PERTANYAAN}</p>
            <textarea class="w-full border p-3 rounded-lg text-sm mb-3 focus:outline-blue-500" rows="3" placeholder="Tulis jawabanmu disini..."></textarea>
            <details class="group">
                <summary class="flex cursor-pointer items-center gap-2 text-orange-600 font-semibold text-sm select-none"><i class="fa-solid fa-book-open"></i> Lihat Jawaban Lengkap</summary>
                <div class="mt-3 bg-orange-50 border-l-4 border-orange-500 p-4 text-sm rounded"><p class="font-bold text-gray-900 mb-1">Pembahasan:</p><p class="text-gray-700 whitespace-pre-line font-mono text-xs md:text-sm">{JAWABAN_LENGKAP}</p></div>
            </details>
        </div>
    </div>
</article>
"""

# --- 2. FUNGSI BIKIN FILE DOCX ---
def create_docx(data, filename_base):
    doc = Document()
    meta = data.get('meta', {})
    
    # Header Dokumen
    judul = doc.add_heading(meta.get('judul_bab', 'Latihan Soal'), 0)
    judul.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"Mapel: {meta.get('mapel')} | Kelas: {meta.get('kelas')} | Jenjang: {meta.get('jenjang')}").bold = True

    doc.add_paragraph("---------------------------------------------------------------------------------------------")

    # BAGIAN A: PG
    doc.add_heading('A. Pilihan Ganda', level=1)
    for q in data.get('soal_pg', []):
        doc.add_paragraph(f"{q['no']}. {q['tanya']}")
        # Opsi (Indent dikit)
        p_opsi = doc.add_paragraph()
        p_opsi.paragraph_format.left_indent = Inches(0.5)
        p_opsi.add_run(f"A. {q['opsi_a']}\n")
        p_opsi.add_run(f"B. {q['opsi_b']}\n")
        p_opsi.add_run(f"C. {q['opsi_c']}\n")
        p_opsi.add_run(f"D. {q['opsi_d']}")

    # BAGIAN B: ESSAY
    doc.add_heading('B. Soal Uraian', level=1)
    for q in data.get('soal_essay', []):
        doc.add_paragraph(f"{q['no']}. {q['tanya']}")
        doc.add_paragraph("\n") # Kasih space buat murid nulis jawaban

    # BAGIAN KUNCI JAWABAN (Di halaman baru)
    doc.add_page_break()
    doc.add_heading('KUNCI JAWABAN & PEMBAHASAN', level=1)
    
    doc.add_heading('Kunci Pilihan Ganda:', level=2)
    for q in data.get('soal_pg', []):
        p = doc.add_paragraph()
        p.add_run(f"{q['no']}. {q['jawaban']}").bold = True
        p.add_run(f" - {q['pembahasan']}")

    doc.add_heading('Kunci Soal Uraian:', level=2)
    for q in data.get('soal_essay', []):
        p = doc.add_paragraph()
        p.add_run(f"{q['no']}. ").bold = True
        p.add_run(f"{q['jawaban_lengkap']}")

    # Simpan File
    os.makedirs('output/downloads', exist_ok=True) # Bikin folder khusus download
    output_path = f"output/downloads/{filename_base}.docx"
    doc.save(output_path)
    return f"downloads/{filename_base}.docx" # Return path relatif buat link HTML

# --- 3. FUNGSI UTAMA GENERATOR ---
def generate_pages():
    try:
        with open('template.html', 'r', encoding='utf-8') as f: template_utama = f.read()
    except FileNotFoundError: return print("❌ Template gak ada Cok!")

    folder_data = 'data'
    os.makedirs('output', exist_ok=True)
    files = [f for f in os.listdir(folder_data) if f.endswith('.json')]

    print(f"🚀 Memproses {len(files)} materi...")

    for filename in files:
        path = os.path.join(folder_data, filename)
        with open(path, 'r', encoding='utf-8') as f: data = json.load(f)

        # 1. GENERATE DOCX DULU
        nama_base = filename.replace('.json', '')
        link_docx = create_docx(data, nama_base) # Dapet link file yg baru dibuat
        print(f"   📄 Dokumen dibuat: {link_docx}")

        # 2. GENERATE HTML (Sama kayak script v2, tapi link downloadnya otomatis)
        meta = data.get('meta', {})
        list_pg = data.get('soal_pg', [])
        list_essay = data.get('soal_essay', [])

        html_pg = ""
        for q in list_pg:
            html_pg += TEMPLATE_PG.format(NO=q['no'], PERTANYAAN=q['tanya'], OPSI_A=q['opsi_a'], OPSI_B=q['opsi_b'], OPSI_C=q['opsi_c'], OPSI_D=q['opsi_d'], JAWABAN=q['jawaban'], PEMBAHASAN=q['pembahasan'])

        html_essay = ""
        for q in list_essay:
            html_essay += TEMPLATE_ESSAY.format(NO=q['no'], PERTANYAAN=q['tanya'], JAWABAN_LENGKAP=q['jawaban_lengkap'])

        # INJECT CONTENT
        konten_full = f"""
        <h2 class="text-xl font-bold text-blue-800 mb-4 border-b pb-2">A. Pilihan Ganda</h2>{html_pg}
        <div class="w-full flex justify-center my-8"><div class="w-[300px] h-[250px] bg-gray-200 flex items-center justify-center text-gray-500 text-sm font-bold border-2 border-dashed border-gray-300">[IKLAN ADSENSE PEMISAH]</div></div>
        <h2 class="text-xl font-bold text-orange-800 mb-4 border-b pb-2">B. Soal Uraian</h2>{html_essay}
        """

        halaman_jadi = template_utama.replace("{{JUDUL_BAB}}", meta.get('judul_bab', ''))\
            .replace("{{JENJANG}}", meta.get('jenjang', ''))\
            .replace("{{MAPEL}}", meta.get('mapel', ''))\
            .replace("{{KELAS}}", meta.get('kelas', ''))\
            .replace("{{LINK_DOWNLOAD}}", link_docx)\
            .replace("{{LIST_SOAL}}", konten_full)

        with open(f'output/{nama_base}.html', 'w', encoding='utf-8') as f: f.write(halaman_jadi)
        print(f"✅ Web selesai: {nama_base}.html")

if __name__ == "__main__":
    generate_pages()
