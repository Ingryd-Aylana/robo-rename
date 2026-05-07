from __future__ import annotations

import re
import sys
import traceback
import unicodedata
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter

APP_NAME = "Robo Rename"
INPUT_DIR_NAME = "entrada"
OUTPUT_DIR_NAME = "saida"
LOG_DIR_NAME = "logs"

CERT_PAT = re.compile(r"\bSP\s+(L\d+(?:-\d+)?)\b", re.IGNORECASE)


def app_root() -> Path:
    """Retorna a pasta onde o executavel/script esta rodando."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def sanitize_filename(text: str) -> str:
    text = text.strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s.-]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ", "_")
    return text[:120] or "SEM_NOME"


def is_address_line(text: str) -> bool:
    return bool(
        re.match(
            r"^(AV|AVENIDA|RUA|TRAVESSA|ALAMEDA|ESTRADA|RODOVIA|PRA[CÇ]A|LARGO)\b",
            text,
            re.IGNORECASE,
        )
    )


def looks_like_name(text: str) -> bool:
    if len(text.strip()) < 5:
        return False

    if is_address_line(text):
        return False

    if re.search(r"R\$|\d{2}/\d{2}/\d{4}|^\d+$", text):
        return False

    blocked_terms = [
        "DEMONSTRATIVO",
        "GARANTIA",
        "GARANTIAS",
        "PROCESSO SUSEP",
        "CERTIFICADO",
        "APÓLICE",
        "APOLICE",
        "VIGÊNCIA",
        "VIGENCIA",
        "DATA DE EMISSÃO",
        "DATA DE EMISSAO",
        "CENTRAL DE ATENDIMENTO",
        "FEDCORP CLUBE DE BENEFÍCIOS",
        "FEDCORP CLUBE DE BENEFICIOS",
        "PAGAMENTO DE ALUGUEL",
        "INCENDIO PREDIO",
        "RESIDENCIAL",
        "APTO",
    ]

    upper = text.upper()
    if any(term in upper for term in blocked_terms):
        return False

    return True


def looks_like_company_line(text: str) -> bool:
    upper = text.upper()
    company_terms = [
        "LTDA",
        "IMOBILI",
        "CONDOM",
        "BENEF",
        "SERVICOS",
        "SERVIÇOS",
        "ADMINISTRAD",
        "NEGOCIOS",
        "NEGÓCIOS",
    ]
    return any(term in upper for term in company_terms)


def extract_name_and_cert(page_text: str) -> tuple[str | None, str | None]:
    text = (page_text or "").replace("\u00a0", " ")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    nome = None
    cert = None

    for line in lines:
        match = CERT_PAT.search(line)
        if match:
            cert = match.group(1)
            break

    # Padrao esperado: [empresa] -> [nome] -> [endereco]
    for i in range(len(lines) - 2):
        empresa = lines[i]
        possivel_nome = lines[i + 1]
        possivel_endereco = lines[i + 2]

        if (
            looks_like_company_line(empresa)
            and looks_like_name(possivel_nome)
            and is_address_line(possivel_endereco)
        ):
            nome = possivel_nome
            break

    return nome, cert


def unique_output_path(out_dir: Path, base_name: str, used_names: set[str]) -> Path:
    filename = f"{base_name}.pdf"
    counter = 1

    while filename in used_names or (out_dir / filename).exists():
        counter += 1
        filename = f"{base_name}__{counter}.pdf"

    used_names.add(filename)
    return out_dir / filename


def process_pdf(pdf_path: Path, out_dir: Path) -> tuple[int, int]:
    reader = PdfReader(str(pdf_path))
    used_names: set[str] = set()
    written = 0
    skipped = 0

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        nome, cert = extract_name_and_cert(text)

        if not nome:
            skipped += 1
            continue

        safe_name = sanitize_filename(nome)
        safe_cert = sanitize_filename(cert) if cert else f"pag{page_number:03d}"
        base_name = f"{safe_name}__{safe_cert}"
        output_path = unique_output_path(out_dir, base_name, used_names)

        writer = PdfWriter()
        writer.add_page(page)

        with output_path.open("wb") as file:
            writer.write(file)

        written += 1

    return written, skipped


def write_log(log_dir: Path, content: str) -> Path:
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"execucao_{timestamp}.txt"
    log_path.write_text(content, encoding="utf-8")
    return log_path


def run() -> int:
    root = app_root()
    entrada_dir = root / INPUT_DIR_NAME
    saida_dir = root / OUTPUT_DIR_NAME
    logs_dir = root / LOG_DIR_NAME

    entrada_dir.mkdir(exist_ok=True)
    saida_dir.mkdir(exist_ok=True)

    pdfs = sorted(entrada_dir.glob("*.pdf")) + sorted(entrada_dir.glob("*.PDF"))
    pdfs = sorted(set(pdfs))

    print(f"=== {APP_NAME} ===")
    print(f"Pasta de entrada: {entrada_dir}")
    print(f"Pasta de saida:   {saida_dir}")
    print()

    if not pdfs:
        message = "Nenhum PDF encontrado na pasta entrada. Coloque os PDFs em entrada/ e rode novamente."
        print(message)
        write_log(logs_dir, message)
        return 0

    total_written = 0
    total_skipped = 0
    errors: list[str] = []
    log_lines: list[str] = [f"{APP_NAME} - {datetime.now():%d/%m/%Y %H:%M:%S}", ""]

    for pdf in pdfs:
        print(f"Processando: {pdf.name}")
        try:
            written, skipped = process_pdf(pdf, saida_dir)
            total_written += written
            total_skipped += skipped
            result = f"OK - {pdf.name}: gerados={written}, paginas_puladas={skipped}"
            print(f"  {result}")
            log_lines.append(result)
        except Exception as exc:  # noqa: BLE001 - log amigavel para usuario final
            error = f"ERRO - {pdf.name}: {exc}"
            errors.append(error)
            print(f"  {error}")
            log_lines.append(error)
            log_lines.append(traceback.format_exc())

    print()
    print("Resumo:")
    print(f"  PDFs encontrados: {len(pdfs)}")
    print(f"  Arquivos gerados: {total_written}")
    print(f"  Paginas puladas:  {total_skipped}")
    print(f"  Erros:            {len(errors)}")

    log_lines.extend(
        [
            "",
            "Resumo:",
            f"PDFs encontrados: {len(pdfs)}",
            f"Arquivos gerados: {total_written}",
            f"Paginas puladas: {total_skipped}",
            f"Erros: {len(errors)}",
        ]
    )
    log_path = write_log(logs_dir, "\n".join(log_lines))
    print(f"Log salvo em: {log_path}")

    return 1 if errors else 0


def main() -> None:
    exit_code = run()
    if getattr(sys, "frozen", False):
        input("\nPressione Enter para fechar...")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
