"""
TEKNOFEST Asistan Studio
- Yerli yarışma takımlarına görev yönetimi, kod üretimi, doküman taslağı ve proje analizi desteği sağlar.
- CustomTkinter arayüzü üzerinde çalışır.
"""

from __future__ import annotations

import ast
import json
import queue
import re
import subprocess
import sys
import threading
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Callable

import customtkinter as ctk
import g4f
from duckduckgo_search import DDGS


# --------------------------------------------------------------------------------------
# Yapılandırma Modelleri
# --------------------------------------------------------------------------------------


@dataclass
class UIConfig:
    app_title: str = "TEKNOFEST Asistan Studio v2"
    geometry: str = "1480x940"
    theme: str = "dark"
    color_theme: str = "dark-blue"


@dataclass
class EngineConfig:
    memory_file: Path = Path("teknofest_memory.json")
    system_log_file: Path = Path("teknofest_system.log")
    max_search_results: int = 5
    llm_timeout: int = 35
    max_history_size: int = 250
    max_console_log_chars: int = 14_000


@dataclass
class OpenClawProfile:
    enabled: bool = True
    mode: str = "Agent"
    model: str = "auto"
    use_web: bool = True
    use_file_ops: bool = True
    use_installer: bool = False
    temperature: float = 0.2


@dataclass
class LanguageRule:
    extension: str
    aliases: tuple[str, ...]


@dataclass
class ProjectSnapshot:
    generated_at: str
    root: str
    file_count: int
    non_empty_line_count: int
    language_distribution: dict[str, int] = field(default_factory=dict)
    discovered_modules: list[str] = field(default_factory=list)
    recommended_installs: list[str] = field(default_factory=list)


@dataclass
class CommandInterpretation:
    raw: str
    normalized: str
    intent: str
    target_filename: str | None
    inferred_extension: str
    should_generate_file: bool
    should_install_module: bool


# --------------------------------------------------------------------------------------
# Sabitler
# --------------------------------------------------------------------------------------


FAST_RESPONSES = {
    "selam": "Merhaba, TEKNOFEST Asistan Studio hazır. Görevinizi iletebilirsiniz.",
    "merhaba": "Merhaba! Projenizin teknik ihtiyaçları için hazırım.",
    "naber": "Sistem stabil. Kod, rapor ve proje yönetimi için destek verebilirim.",
    "kimsin": "Ben TEKNOFEST Asistan Studio; yarışma odaklı mühendislik asistanıyım.",
}

INSTANT_COMMANDS = {
    "hello": "Hi.",
    "hi": "Hi.",
    "ping": "pong",
    "status": "online",
    "thanks": "You're welcome.",
}

FILE_CREATION_KEYWORDS = {
    "oluştur",
    "yaz",
    "üret",
    "kaydet",
    "ekle",
    "hazırla",
    "generate",
    "create",
    "build",
}

INSTALL_KEYWORDS = {
    "kur",
    "yükle",
    "install",
    "pip",
}

ALLOWED_INSTALL_PATTERN = re.compile(r"^[a-zA-Z0-9_.\-]+$")

LANGUAGE_RULES = [
    LanguageRule(".py", ("python", "py", "script", "kod")),
    LanguageRule(".html", ("html", "web", "sayfa", "frontend")),
    LanguageRule(".css", ("css", "stil", "tasarım")),
    LanguageRule(".js", ("javascript", "js", "node")),
    LanguageRule(".ts", ("typescript", "ts")),
    LanguageRule(".json", ("json", "veri", "schema")),
    LanguageRule(".md", ("markdown", "doküman", "rapor", "readme", "md")),
    LanguageRule(".txt", ("not", "text", "metin")),
]

SYSTEM_PROMPT = (
    "You are a senior autonomous polyglot software engineer AI. "
    "Auto-detect requested programming language and use idiomatic production-grade code. "
    "If language is unspecified, choose the most suitable language and output executable code only. "
    "For simple greeting/commands (hello, hi, ping, status, thanks), answer instantly without explanation. "
    "Never output pseudocode or incomplete snippets. "
    "Use minimal comments, basic error handling, secure defaults, and scalable async patterns when appropriate. "
    "For complex implementations include modular architecture, file structure, and usage. "
    "Prefer the most scalable and maintainable solution with concise output."
)


# --------------------------------------------------------------------------------------
# Servis Katmanı
# --------------------------------------------------------------------------------------


class EventBus:
    """Thread-safe UI güncellemeleri için kuyruk tabanlı olay taşıyıcısı."""

    def __init__(self):
        self._queue: queue.Queue[tuple[str, tuple[Any, ...]]] = queue.Queue()

    def emit(self, action: str, *payload: Any) -> None:
        self._queue.put((action, payload))

    def drain(self) -> list[tuple[str, tuple[Any, ...]]]:
        out: list[tuple[str, tuple[Any, ...]]] = []
        while True:
            try:
                out.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return out


class MemoryStore:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, Any] = {
            "history": [],
            "short_cache": {},
            "workspace_notes": {},
            "created_files": [],
        }

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self.data = {
                "history": [],
                "short_cache": {},
                "workspace_notes": {},
                "created_files": [],
            }

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def cache_get(self, key: str) -> str | None:
        return self.data.setdefault("short_cache", {}).get(key)

    def cache_set(self, key: str, value: str) -> None:
        self.data.setdefault("short_cache", {})[key] = value

    def add_history(self, item: dict[str, Any], max_size: int) -> None:
        hist = self.data.setdefault("history", [])
        hist.append(item)
        if len(hist) > max_size:
            self.data["history"] = hist[-max_size:]

    def add_created_file(self, path: str) -> None:
        arr = self.data.setdefault("created_files", [])
        arr.append({"path": path, "at": int(time.time())})


class SystemLogger:
    def __init__(self, path: Path, emit: Callable[[str], None]):
        self.path = path
        self.emit = emit

    def log(self, text: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {text}\n"
        try:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
        self.emit(text)


class ProjectAnalyzer:
    def __init__(self, logger: SystemLogger):
        self.logger = logger

    def scan(self, workspace: Path) -> ProjectSnapshot:
        files = [p for p in workspace.iterdir() if p.is_file()]
        language_counter: Counter[str] = Counter()
        discovered_imports: set[str] = set()
        non_empty_lines = 0

        for file_path in files:
            ext = file_path.suffix.lower() or "[uzantısız]"
            language_counter[ext] += 1
            line_count, imports = self._analyze_file(file_path)
            non_empty_lines += line_count
            discovered_imports.update(imports)

        recommended = sorted(self._filter_external_packages(discovered_imports))

        snapshot = ProjectSnapshot(
            generated_at=datetime.now().isoformat(timespec="seconds"),
            root=str(workspace),
            file_count=len(files),
            non_empty_line_count=non_empty_lines,
            language_distribution=dict(language_counter),
            discovered_modules=sorted(discovered_imports),
            recommended_installs=recommended,
        )
        self.logger.log("Proje analizi tamamlandı.")
        return snapshot

    def _analyze_file(self, path: Path) -> tuple[int, set[str]]:
        imports: set[str] = set()
        non_empty = 0
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            non_empty = sum(1 for line in content.splitlines() if line.strip())
            if path.suffix.lower() == ".py":
                imports = self._parse_python_imports(content)
        except Exception as exc:
            self.logger.log(f"Dosya okunamadı: {path.name} ({exc})")
        return non_empty, imports

    @staticmethod
    def _parse_python_imports(code: str) -> set[str]:
        out: set[str] = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        out.add(n.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    out.add(node.module.split(".")[0])
        except SyntaxError:
            # Regex fallback
            hits = re.findall(r"^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)", code, re.MULTILINE)
            out.update(hits)
        return out

    @staticmethod
    def _filter_external_packages(imports: set[str]) -> set[str]:
        std = set(sys.builtin_module_names)
        local_ignored = {
            "os",
            "sys",
            "time",
            "json",
            "re",
            "pathlib",
            "threading",
            "typing",
            "collections",
            "dataclasses",
            "datetime",
            "subprocess",
            "tkinter",
        }
        return {m for m in imports if m not in std and m not in local_ignored and not m.startswith("_")}


class SearchService:
    def __init__(self, logger: SystemLogger, max_results: int):
        self.logger = logger
        self.max_results = max_results

    def query(self, text: str) -> str:
        self.logger.log("Web araştırması başlatıldı.")
        try:
            with DDGS() as ddgs:
                records: list[str] = []
                for row in ddgs.text(text, max_results=self.max_results):
                    title = row.get("title", "Başlık yok")
                    body = row.get("body", "")
                    records.append(f"- {title}: {body}")
                if not records:
                    return "Web sonucu bulunamadı."
                return "\n".join(records)
        except Exception as exc:
            self.logger.log(f"Web araştırması başarısız: {exc}")
            return "Web araştırması başarısız oldu."


class AIEngine:
    def __init__(self, logger: SystemLogger, timeout: int):
        self.logger = logger
        self.timeout = timeout

    def ask(
        self,
        user_command: str,
        web_context: str,
        project_context: str,
        language_hint: str,
        mode: str,
        selected_model: str,
        temperature: float,
    ) -> str:
        self.logger.log("LLM yanıtı hazırlanıyor.")
        try:
            msg = (
                f"Detected language: {language_hint}\n\n"
                f"Execution mode: {mode}\n"
                f"Selected profile model: {selected_model}\n"
                f"Temperature target: {temperature:.2f}\n\n"
                f"Proje bağlamı:\n{project_context}\n\n"
                f"Web bağlamı:\n{web_context}\n\n"
                f"Kullanıcı komutu:\n{user_command}"
            )
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": msg},
                ],
                timeout=self.timeout,
            )
            if isinstance(response, str):
                return response
            return str(response)
        except Exception as exc:
            self.logger.log(f"LLM hatası: {exc}")
            return (
                "AI motoruna erişilemedi. Aşağıdaki bağlam ile manuel ilerleyebilirsiniz:\n\n"
                f"{web_context}"
            )


class InstallerService:
    def __init__(self, logger: SystemLogger):
        self.logger = logger

    def install_package(self, package_name: str) -> tuple[bool, str]:
        if not package_name or not ALLOWED_INSTALL_PATTERN.match(package_name):
            return False, "Geçersiz paket adı."

        self.logger.log(f"Paket kurulumu başlatıldı: {package_name}")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode == 0:
                return True, f"{package_name} başarıyla kuruldu."
            msg = completed.stderr.strip() or completed.stdout.strip()
            return False, f"Kurulum başarısız (kod={completed.returncode}): {msg[:300]}"
        except Exception as exc:
            return False, f"Kurulum sırasında hata: {exc}"


class FileArchitect:
    def __init__(self, logger: SystemLogger):
        self.logger = logger

    def infer_extension(self, command: str) -> str:
        normalized = command.lower()
        for rule in LANGUAGE_RULES:
            if any(alias in normalized for alias in rule.aliases):
                return rule.extension
        return ".txt"

    def extract_filename(self, command: str) -> str | None:
        match = re.search(r"([\w\- ]+\.(?:py|html|css|js|ts|json|md|txt))", command, flags=re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip().replace(" ", "_")

    @staticmethod
    def cleanup_markdown_code(content: str) -> str:
        blocks = re.findall(r"```(?:[a-zA-Z0-9_+\-]*)\n(.*?)```", content, re.DOTALL)
        if blocks:
            return "\n\n".join(b.strip() for b in blocks)
        return content.strip()

    def save_generated_content(self, workspace: Path, command: str, model_output: str) -> Path:
        ext = self.infer_extension(command)
        filename = self.extract_filename(command) or f"teknofest_output_{int(time.time())}{ext}"
        final_path = (workspace / filename).resolve()
        workspace_resolved = workspace.resolve()
        if workspace_resolved not in final_path.parents and final_path != workspace_resolved:
            raise ValueError("Geçersiz dosya yolu algılandı.")

        clean_text = self.cleanup_markdown_code(model_output)
        final_path.write_text(clean_text + "\n", encoding="utf-8")
        self.logger.log(f"Dosya oluşturuldu: {final_path.name}")
        return final_path


class CommandRouter:
    def interpret(self, command: str) -> CommandInterpretation:
        normalized = command.lower().strip()
        target_filename = self._extract_filename(normalized)
        inferred_ext = self._infer_ext(normalized)

        should_generate_file = any(k in normalized for k in FILE_CREATION_KEYWORDS)
        should_install_module = any(k in normalized for k in INSTALL_KEYWORDS)

        if should_install_module:
            intent = "install"
        elif should_generate_file:
            intent = "create"
        elif normalized in FAST_RESPONSES:
            intent = "quick"
        else:
            intent = "ask"

        return CommandInterpretation(
            raw=command,
            normalized=normalized,
            intent=intent,
            target_filename=target_filename,
            inferred_extension=inferred_ext,
            should_generate_file=should_generate_file,
            should_install_module=should_install_module,
        )

    @staticmethod
    def _extract_filename(command: str) -> str | None:
        match = re.search(r"([\w\- ]+\.(?:py|html|css|js|ts|json|md|txt))", command, flags=re.IGNORECASE)
        return match.group(1).strip().replace(" ", "_") if match else None

    @staticmethod
    def _infer_ext(command: str) -> str:
        for rule in LANGUAGE_RULES:
            if any(alias in command for alias in rule.aliases):
                return rule.extension
        return ".txt"

    @staticmethod
    def detect_language_name(command: str) -> str:
        lower = command.lower()
        mapping = {
            "python": "Python",
            "py": "Python",
            "javascript": "JavaScript",
            "js": "JavaScript",
            "typescript": "TypeScript",
            "ts": "TypeScript",
            "html": "HTML",
            "css": "CSS",
            "json": "JSON",
            "markdown": "Markdown",
            "md": "Markdown",
            "go": "Go",
            "golang": "Go",
            "rust": "Rust",
            "java": "Java",
            "c#": "C#",
            "c++": "C++",
            "php": "PHP",
            "ruby": "Ruby",
            "kotlin": "Kotlin",
            "swift": "Swift",
        }
        for key, val in mapping.items():
            if key in lower:
                return val
        return "Auto"


# --------------------------------------------------------------------------------------
# UI Uygulaması
# --------------------------------------------------------------------------------------


class TeknofestAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # config
        self.ui_cfg = UIConfig()
        self.engine_cfg = EngineConfig()
        self.openclaw = OpenClawProfile()

        # services
        self.bus = EventBus()
        self.memory = MemoryStore(self.engine_cfg.memory_file)
        self.memory.load()

        self.logger = SystemLogger(self.engine_cfg.system_log_file, lambda msg: self.bus.emit("system_log", msg))
        self.analyzer = ProjectAnalyzer(self.logger)
        self.search = SearchService(self.logger, self.engine_cfg.max_search_results)
        self.ai = AIEngine(self.logger, self.engine_cfg.llm_timeout)
        self.installer = InstallerService(self.logger)
        self.architect = FileArchitect(self.logger)
        self.router = CommandRouter()

        # state
        self.workspace: Path | None = None
        self.snapshot: ProjectSnapshot | None = None
        self.pending_install: set[str] = set()
        self.command_history: list[str] = []

        # setup ui
        self._setup_main_window()
        self._build_layout_frames()
        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

        # bootstrap
        self._append_chat("ASİSTAN", "TEKNOFEST Asistan Studio hazır. Çalışma klasörü seçip görev verebilirsiniz.")
        self.logger.log("Uygulama başlatıldı.")
        self.after(120, self._drain_events)

    # ----------------- UI Setup -----------------

    def _setup_main_window(self) -> None:
        self.title(self.ui_cfg.app_title)
        self.geometry(self.ui_cfg.geometry)
        ctk.set_appearance_mode(self.ui_cfg.theme)
        ctk.set_default_color_theme(self.ui_cfg.color_theme)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_layout_frames(self) -> None:
        self.left = ctk.CTkFrame(self, fg_color="#14161a", corner_radius=0)
        self.center = ctk.CTkFrame(self, fg_color="#0f1115")
        self.right = ctk.CTkFrame(self, fg_color="#14161a", corner_radius=0)

        self.left.grid(row=0, column=0, sticky="nsew", padx=(6, 4), pady=6)
        self.center.grid(row=0, column=1, sticky="nsew", padx=4, pady=6)
        self.right.grid(row=0, column=2, sticky="nsew", padx=(4, 6), pady=6)

    def _build_left_panel(self) -> None:
        ctk.CTkLabel(
            self.left,
            text="TEKNOFEST\nKONTROL PANELİ",
            font=("Segoe UI", 24, "bold"),
            text_color="#00d4ff",
            justify="center",
        ).pack(pady=(18, 10))

        self.btn_workspace = ctk.CTkButton(
            self.left,
            text="📁 Çalışma Alanı Seç",
            command=self.select_workspace,
            height=42,
            fg_color="#1f6aa5",
            hover_color="#195988",
        )
        self.btn_workspace.pack(fill="x", padx=14, pady=6)

        self.lbl_workspace = ctk.CTkLabel(self.left, text="Yol: seçilmedi", font=("Consolas", 10), text_color="#a9a9a9")
        self.lbl_workspace.pack(fill="x", padx=14)

        self.btn_refresh = ctk.CTkButton(
            self.left,
            text="🔄 Proje Analizini Yenile",
            command=self.refresh_project_analysis,
            height=38,
            fg_color="#245f4a",
            hover_color="#1d4f3d",
        )
        self.btn_refresh.pack(fill="x", padx=14, pady=(10, 6))

        self.btn_install = ctk.CTkButton(
            self.left,
            text="📦 Önerilen Paketleri Kur",
            command=self.install_recommended_packages,
            height=38,
            fg_color="#8a6a1e",
            hover_color="#715718",
        )
        self.btn_install.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(self.left, text="OpenClaw Uyum Modu", font=("Consolas", 12, "bold")).pack(anchor="w", padx=14)
        self.openclaw_enabled = ctk.BooleanVar(value=self.openclaw.enabled)
        self.openclaw_toggle = ctk.CTkSwitch(
            self.left,
            text="OpenClaw benzeri akış aktif",
            variable=self.openclaw_enabled,
            command=self._apply_openclaw_settings,
        )
        self.openclaw_toggle.pack(fill="x", padx=14, pady=(2, 6))

        self.mode_selector = ctk.CTkSegmentedButton(
            self.left,
            values=["Agent", "Chat"],
            command=lambda v: self._set_mode(v),
        )
        self.mode_selector.set(self.openclaw.mode)
        self.mode_selector.pack(fill="x", padx=14, pady=(0, 6))

        self.model_selector = ctk.CTkOptionMenu(
            self.left,
            values=["auto", "coder", "reasoner", "fast"],
            command=self._set_model,
        )
        self.model_selector.set(self.openclaw.model)
        self.model_selector.pack(fill="x", padx=14, pady=(0, 6))

        self.temperature_slider = ctk.CTkSlider(self.left, from_=0.0, to=1.0, command=self._set_temperature)
        self.temperature_slider.set(self.openclaw.temperature)
        self.temperature_slider.pack(fill="x", padx=14, pady=(0, 6))

        self.temp_label = ctk.CTkLabel(self.left, text=f"Sıcaklık: {self.openclaw.temperature:.2f}", font=("Consolas", 10))
        self.temp_label.pack(anchor="w", padx=14, pady=(0, 6))

        self.web_enabled = ctk.BooleanVar(value=self.openclaw.use_web)
        self.file_enabled = ctk.BooleanVar(value=self.openclaw.use_file_ops)
        self.install_enabled = ctk.BooleanVar(value=self.openclaw.use_installer)

        ctk.CTkCheckBox(self.left, text="Web arama", variable=self.web_enabled, command=self._apply_openclaw_settings).pack(
            anchor="w", padx=14
        )
        ctk.CTkCheckBox(self.left, text="Dosya işlemleri", variable=self.file_enabled, command=self._apply_openclaw_settings).pack(
            anchor="w", padx=14
        )
        ctk.CTkCheckBox(self.left, text="Paket kurulum", variable=self.install_enabled, command=self._apply_openclaw_settings).pack(
            anchor="w", padx=14, pady=(0, 8)
        )

        ctk.CTkLabel(self.left, text="Sistem Günlüğü", font=("Consolas", 12, "bold")).pack(anchor="w", padx=14)
        self.system_log_text = ctk.CTkTextbox(self.left, height=260, font=("Consolas", 10), fg_color="#08090b")
        self.system_log_text.pack(fill="both", expand=True, padx=14, pady=(4, 10))

        ctk.CTkLabel(self.left, text="Dil Dağılımı", font=("Consolas", 12, "bold")).pack(anchor="w", padx=14)
        self.stats_text = ctk.CTkTextbox(self.left, height=140, font=("Consolas", 10), fg_color="#08090b")
        self.stats_text.pack(fill="x", padx=14, pady=(4, 14))

    def _build_center_panel(self) -> None:
        ctk.CTkLabel(
            self.center,
            text="OpenClaw Benzeri Mühendislik Konsolu",
            font=("Segoe UI", 18, "bold"),
            text_color="#bce8ff",
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.quick_frame = ctk.CTkFrame(self.center, fg_color="transparent")
        self.quick_frame.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkButton(
            self.quick_frame,
            text="PRD Taslağı",
            width=120,
            command=lambda: self._inject_template("Bir ürün gereksinim dokümanı (PRD) şablonu hazırla."),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            self.quick_frame,
            text="API İskeleti",
            width=120,
            command=lambda: self._inject_template("Python FastAPI ile production API iskeleti oluştur."),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            self.quick_frame,
            text="Test Paketi",
            width=120,
            command=lambda: self._inject_template("Proje için birim test paketi üret."),
        ).pack(side="left")

        self.chat_box = ctk.CTkTextbox(
            self.center,
            state="disabled",
            fg_color="#050608",
            font=("Consolas", 13),
            text_color="#d7f9ff",
            wrap="word",
        )
        self.chat_box.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.input_frame = ctk.CTkFrame(self.center, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.command_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Komut girin (örn: main.py içinde Flask API iskeleti oluştur)",
            height=44,
            font=("Segoe UI", 13),
        )
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.command_entry.bind("<Return>", lambda e: self.submit_command())

        self.submit_button = ctk.CTkButton(
            self.input_frame,
            text="▶ Çalıştır",
            command=self.submit_command,
            width=120,
            height=44,
            fg_color="#1f6aa5",
            hover_color="#195988",
        )
        self.submit_button.pack(side="right")

    def _build_right_panel(self) -> None:
        ctk.CTkLabel(
            self.right,
            text="Proje Gezgini",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffd479",
        ).pack(pady=(16, 8))

        self.file_tree = ctk.CTkTextbox(self.right, font=("Consolas", 11), fg_color="#08090b")
        self.file_tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        ctk.CTkLabel(self.right, text="Komut Geçmişi", font=("Consolas", 12, "bold")).pack(anchor="w", padx=12)
        self.history_list = ctk.CTkTextbox(self.right, height=120, font=("Consolas", 10), fg_color="#08090b")
        self.history_list.pack(fill="x", padx=12, pady=(4, 8))

        ctk.CTkLabel(self.right, text="Bulunan Modüller", font=("Consolas", 12, "bold")).pack(anchor="w", padx=12)
        self.module_list = ctk.CTkTextbox(self.right, height=150, font=("Consolas", 10), fg_color="#08090b")
        self.module_list.pack(fill="x", padx=12, pady=(4, 8))

        ctk.CTkLabel(self.right, text="Önerilen Kurulumlar", font=("Consolas", 12, "bold")).pack(anchor="w", padx=12)
        self.recommended_list = ctk.CTkTextbox(self.right, height=150, font=("Consolas", 10), fg_color="#08090b")
        self.recommended_list.pack(fill="x", padx=12, pady=(4, 10))

        self.btn_save_memory = ctk.CTkButton(
            self.right,
            text="🧠 Hafızayı Kaydet",
            command=self.save_memory,
            fg_color="#355e3b",
            hover_color="#2d4f32",
        )
        self.btn_save_memory.pack(fill="x", padx=12, pady=(0, 12))

    # ----------------- UI Thread helpers -----------------

    def _drain_events(self) -> None:
        for action, payload in self.bus.drain():
            if action == "system_log":
                self._append_system_log(payload[0])
            elif action == "chat":
                self._append_chat(payload[0], payload[1])
            elif action == "refresh_analysis":
                self._render_snapshot(payload[0])
            elif action == "refresh_file_tree":
                self._refresh_file_tree()
        self.after(120, self._drain_events)

    def _append_system_log(self, text: str) -> None:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {text}\n"
        self.system_log_text.insert("end", line)
        if len(self.system_log_text.get("1.0", "end")) > self.engine_cfg.max_console_log_chars:
            self.system_log_text.delete("1.0", "10.0")
        self.system_log_text.see("end")

    def _append_chat(self, role: str, text: str) -> None:
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"[{role}]\n{text}\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    # ----------------- Actions -----------------

    def _apply_openclaw_settings(self) -> None:
        self.openclaw.enabled = bool(self.openclaw_enabled.get())
        self.openclaw.use_web = bool(self.web_enabled.get())
        self.openclaw.use_file_ops = bool(self.file_enabled.get())
        self.openclaw.use_installer = bool(self.install_enabled.get())
        self.logger.log(
            f"OpenClaw profil güncellendi: mode={self.openclaw.mode}, model={self.openclaw.model}, "
            f"web={self.openclaw.use_web}, file={self.openclaw.use_file_ops}, install={self.openclaw.use_installer}"
        )

    def _set_mode(self, value: str) -> None:
        self.openclaw.mode = value
        self._apply_openclaw_settings()

    def _set_model(self, value: str) -> None:
        self.openclaw.model = value
        self._apply_openclaw_settings()

    def _set_temperature(self, value: float) -> None:
        self.openclaw.temperature = float(value)
        self.temp_label.configure(text=f"Sıcaklık: {self.openclaw.temperature:.2f}")

    def _inject_template(self, content: str) -> None:
        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, content)

    def select_workspace(self) -> None:
        selected = filedialog.askdirectory()
        if not selected:
            self.logger.log("Çalışma alanı seçimi iptal edildi.")
            return

        self.workspace = Path(selected)
        trimmed = str(self.workspace)
        self.lbl_workspace.configure(text=f"Yol: {trimmed if len(trimmed) < 52 else '...' + trimmed[-52:]}")
        self.logger.log(f"Çalışma alanı seçildi: {self.workspace}")
        self.refresh_project_analysis()

    def refresh_project_analysis(self) -> None:
        if not self.workspace:
            messagebox.showwarning("TEKNOFEST Asistan", "Lütfen önce çalışma alanı seçin.")
            return

        def task() -> None:
            self.logger.log("Proje analizi başlatıldı.")
            snapshot = self.analyzer.scan(self.workspace)
            self.snapshot = snapshot
            self.bus.emit("refresh_analysis", snapshot)
            self.bus.emit("refresh_file_tree")

        threading.Thread(target=task, daemon=True).start()

    def install_recommended_packages(self) -> None:
        if not self.snapshot or not self.snapshot.recommended_installs:
            self.bus.emit("chat", "ASİSTAN", "Kurulacak öneri paketi bulunamadı.")
            return

        packages = list(self.snapshot.recommended_installs)
        self.bus.emit("chat", "ASİSTAN", f"{len(packages)} paket için kurulum başlatıldı.")

        def task() -> None:
            for pkg in packages:
                ok, info = self.installer.install_package(pkg)
                if ok:
                    self.logger.log(info)
                    self.bus.emit("chat", "SİSTEM", f"✅ {info}")
                else:
                    self.logger.log(info)
                    self.bus.emit("chat", "SİSTEM", f"❌ {info}")
            self.bus.emit("chat", "ASİSTAN", "Paket kurulum turu tamamlandı.")
            self.refresh_project_analysis()

        threading.Thread(target=task, daemon=True).start()

    def submit_command(self) -> None:
        raw = self.command_entry.get().strip()
        if not raw:
            return

        self.command_entry.delete(0, "end")
        self.bus.emit("chat", "KULLANICI", raw)
        self.command_history.append(raw)
        self.command_history = self.command_history[-40:]
        self.history_list.delete("1.0", "end")
        self.history_list.insert("end", "\n".join(self.command_history[-12:]))

        interpretation = self.router.interpret(raw)
        threading.Thread(target=self._process_command, args=(interpretation,), daemon=True).start()

    def _process_command(self, interpretation: CommandInterpretation) -> None:
        normalized = interpretation.normalized

        if normalized in INSTANT_COMMANDS:
            self.bus.emit("chat", "ASİSTAN", INSTANT_COMMANDS[normalized])
            return

        # hızlı yanıt
        if normalized in FAST_RESPONSES:
            resp = FAST_RESPONSES[normalized]
            self.memory.cache_set(normalized, resp)
            self.bus.emit("chat", "ASİSTAN", resp)
            self.logger.log("Hızlı yanıt döndürüldü.")
            return

        cached = self.memory.cache_get(normalized)
        if cached:
            self.bus.emit("chat", "ASİSTAN", f"(Önbellekten)\n{cached}")
            self.logger.log("Yanıt önbellekten döndürüldü.")
            return

        # install intent
        if interpretation.should_install_module:
            if not self.openclaw.use_installer:
                self.bus.emit("chat", "ASİSTAN", "OpenClaw profilinde paket kurulum devre dışı.")
                return
            package = self._extract_install_target(interpretation.raw)
            if package:
                ok, info = self.installer.install_package(package)
                icon = "✅" if ok else "❌"
                self.bus.emit("chat", "ASİSTAN", f"{icon} {info}")
                self.logger.log(info)
                self.refresh_project_analysis()
                return
            self.bus.emit("chat", "ASİSTAN", "Kurulacak paket adı anlaşılamadı.")

        # context üret
        web_context = self.search.query(interpretation.raw) if self.openclaw.use_web else "Web arama profilde kapalı."
        project_context = self._build_project_context()
        language_hint = self.router.detect_language_name(interpretation.raw)
        ai_response = self.ai.ask(
            interpretation.raw,
            web_context,
            project_context,
            language_hint,
            self.openclaw.mode,
            self.openclaw.model,
            self.openclaw.temperature,
        )

        # dosya üretimi
        created_path: Path | None = None
        if interpretation.should_generate_file:
            if not self.openclaw.use_file_ops:
                self.bus.emit("chat", "ASİSTAN", "OpenClaw profilinde dosya üretimi devre dışı.")
                return
            if not self.workspace:
                self.bus.emit("chat", "ASİSTAN", "Dosya oluşturmak için önce çalışma alanı seçin.")
            else:
                try:
                    created_path = self.architect.save_generated_content(self.workspace, interpretation.raw, ai_response)
                    self.memory.add_created_file(str(created_path))
                    self.bus.emit("chat", "SİSTEM", f"✅ Dosya oluşturuldu: {created_path.name}")
                    self.bus.emit("refresh_file_tree")
                except Exception as exc:
                    self.bus.emit("chat", "SİSTEM", f"❌ Dosya oluşturma hatası: {exc}")

        # yanıt ve bellek
        self.bus.emit("chat", "ASİSTAN", ai_response)
        self.memory.cache_set(normalized, ai_response)
        self.memory.add_history(
            {
                "time": int(time.time()),
                "command": interpretation.raw,
                "intent": interpretation.intent,
                "created_file": str(created_path) if created_path else None,
            },
            max_size=self.engine_cfg.max_history_size,
        )
        self.save_memory(silent=True)

    def _build_project_context(self) -> str:
        if not self.snapshot:
            return "Çalışma alanı analizi mevcut değil."

        lines = [
            f"Klasör: {self.snapshot.root}",
            f"Toplam dosya: {self.snapshot.file_count}",
            f"Boş olmayan satır: {self.snapshot.non_empty_line_count}",
            "Dil dağılımı:",
        ]
        for ext, count in sorted(self.snapshot.language_distribution.items(), key=lambda x: x[0]):
            lines.append(f"  - {ext}: {count}")

        if self.snapshot.recommended_installs:
            lines.append("Önerilen paketler: " + ", ".join(self.snapshot.recommended_installs))
        return "\n".join(lines)

    @staticmethod
    def _extract_install_target(command: str) -> str | None:
        lower = command.lower()
        cleaned = (
            lower.replace("pip install", "")
            .replace("install", "")
            .replace("yükle", "")
            .replace("kur", "")
            .strip()
        )
        match = re.search(r"[a-zA-Z0-9_.\-]+", cleaned)
        return match.group(0) if match else None

    def save_memory(self, silent: bool = False) -> None:
        try:
            self.memory.save()
            if not silent:
                messagebox.showinfo("TEKNOFEST Asistan", "Hafıza başarıyla kaydedildi.")
            self.logger.log("Hafıza kaydedildi.")
        except Exception as exc:
            self.logger.log(f"Hafıza kaydedilemedi: {exc}")
            if not silent:
                messagebox.showerror("TEKNOFEST Asistan", f"Hafıza kaydı başarısız: {exc}")

    # ----------------- UI renderers -----------------

    def _render_snapshot(self, snapshot: ProjectSnapshot) -> None:
        self.stats_text.delete("1.0", "end")
        total = max(snapshot.file_count, 1)
        for ext, count in sorted(snapshot.language_distribution.items(), key=lambda x: x[1], reverse=True):
            percent = (count / total) * 100
            self.stats_text.insert("end", f"{ext:>8}: {count:>3} dosya  (%{percent:4.1f})\n")

        self.module_list.delete("1.0", "end")
        if snapshot.discovered_modules:
            self.module_list.insert("end", "\n".join(snapshot.discovered_modules))
        else:
            self.module_list.insert("end", "Modül bulunamadı.")

        self.recommended_list.delete("1.0", "end")
        if snapshot.recommended_installs:
            self.recommended_list.insert("end", "\n".join(snapshot.recommended_installs))
        else:
            self.recommended_list.insert("end", "Kurulum önerisi yok.")

    def _refresh_file_tree(self) -> None:
        self.file_tree.delete("1.0", "end")
        if not self.workspace:
            self.file_tree.insert("end", "Çalışma alanı seçilmedi.")
            return

        def collect(root: Path) -> list[str]:
            rows: list[str] = []
            for path in sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                if path.is_dir():
                    rows.append(f"📁 {path.name}")
                    for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                        mark = "📄" if child.is_file() else "📁"
                        rows.append(f"   {mark} {child.name}")
                else:
                    rows.append(f"📄 {path.name}")
            return rows

        try:
            rows = collect(self.workspace)
            self.file_tree.insert("end", "\n".join(rows) if rows else "Klasör boş.")
        except Exception as exc:
            self.file_tree.insert("end", f"Dosya ağacı okunamadı: {exc}")


# --------------------------------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------------------------------


def main() -> None:
    app = TeknofestAssistantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
